import os
import csv
import logging
from datetime import datetime
import requests
import matplotlib.pyplot as plt
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)

CSV_FILE = "gold_prices.csv"

def fetch_gold_price():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto("https://www.grtjewels.com", wait_until="domcontentloaded")
            page.wait_for_timeout(5000)  # Increased from 3000 to 5000ms

            # Try multiple selectors in case the website changed
            selectors = [
                "text=GOLD 22 KT/1g",
                "text=22 KT/1g",
                "[data-price]",  # If they use data attributes
                ".gold-price",   # If they use CSS classes
            ]

            gold_price_text = None
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=5000):
                        gold_price_text = element.text_content()
                        logging.info(f"Found element with selector '{selector}': '{gold_price_text}'")
                        break
                except Exception:
                    continue

            if gold_price_text:
                try:
                    # More robust parsing - look for price patterns (avoid "22 KT")
                    import re
                    # Look for ₹ followed by numbers, or just numbers that are > 1000 (to avoid "22")
                    price_match = re.search(r'₹?\s*([1-9]\d{3,}[\d,]*\.?\d*)', gold_price_text)
                    if price_match:
                        price_str = price_match.group(1).replace(',', '')
                        price_float = float(price_str)
                        # Additional check: gold prices should be reasonable (> 1000)
                        if price_float > 1000:
                            browser.close()
                            return price_float
                        else:
                            logging.warning(f"Price {price_float} seems too low, might be incorrect")
                            browser.close()
                            return None
                    else:
                        logging.error(f"No valid price pattern found in: {gold_price_text}")
                        browser.close()
                        return None
                except Exception as e:
                    logging.error(f"Parsing failed: {gold_price_text} - Error: {e}")
                    browser.close()
                    return None
            else:
                logging.error("Gold price element not found with any selector")
                # Debug: Save page content for inspection
                page_content = page.content()
                with open("debug_page.html", "w") as f:
                    f.write(page_content)
                logging.info("Saved page content to debug_page.html for inspection")
                browser.close()
                return None

    except Exception as e:
        logging.error(f"Scraping error: {e}")
        return None


def save_price(price):
    file_exists = os.path.exists(CSV_FILE)
    is_empty = not file_exists or os.path.getsize(CSV_FILE) == 0

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if is_empty:
            writer.writerow(["timestamp", "price"])

        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), price])


def load_history():
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        return [], []

    timestamps, prices = [], []

    with open(CSV_FILE) as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None or "timestamp" not in reader.fieldnames or "price" not in reader.fieldnames:
            return [], []

        for row in reader:
            timestamps.append(row["timestamp"])
            prices.append(float(row["price"]))

    return timestamps, prices


def generate_plot(timestamps, prices):
    if len(prices) < 2:
        return None

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, prices, marker='o')
    plt.title("Gold Price History")
    plt.xlabel("Time")
    plt.ylabel("Price (₹ per 1g 22K)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    image_path = "gold_price_history.png"
    plt.savefig(image_path)
    plt.close()

    return image_path


def get_trend(prices):
    if len(prices) < 2:
        return ""

    if prices[-1] > prices[-2]:
        return "📈 Increased"
    elif prices[-1] < prices[-2]:
        return "📉 Decreased"
    else:
        return "➖ No Change"


def send_telegram_message(message):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logging.error("Telegram credentials missing")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}

    try:
        requests.post(url, data=data)
    except Exception as e:
        logging.error(f"Telegram message failed: {e}")


def send_telegram_image(image_path):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logging.error("Telegram credentials missing")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

    try:
        with open(image_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": chat_id}
            requests.post(url, files=files, data=data)
    except Exception as e:
        logging.error(f"Telegram image failed: {e}")


if __name__ == "__main__":
    print("Starting gold price scraper...")
    price = fetch_gold_price()
    print(f"Fetched price: {price}")

    if price:
        save_price(price)
        print(f"Saved price {price} to CSV")

        timestamps, prices = load_history()
        trend = get_trend(prices)
        print(f"Trend: {trend}")

        message = f"💰 Gold Price: ₹{price}\n{trend}"
        print(f"Message to send: {message}")
    else:
        message = "⚠️ Could not fetch today's gold price."
        print("Failed to fetch price")

    send_telegram_message(message)
    print("Attempted to send Telegram message")

    timestamps, prices = load_history()
    print(f"Loaded {len(prices)} historical prices")

    if len(prices) >= 2:
        image_path = generate_plot(timestamps, prices)
        if image_path:
            send_telegram_image(image_path)
            print(f"Generated and sent chart: {image_path}")
        else:
            print("Failed to generate chart")
    else:
        logging.info("Not enough data for trend graph yet.")
        print("Not enough data for trend graph yet.")
