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
            page.wait_for_timeout(3000)

            gold_price_button = page.locator("text=GOLD 22 KT/1g").first

            if gold_price_button:
                gold_price_text = gold_price_button.text_content()

                try:
                    price_part = gold_price_text.split('-')[1].strip()
                    price_part = price_part.replace('₹', '').replace(',', '')
                    browser.close()
                    return float(price_part)
                except Exception:
                    logging.error(f"Parsing failed: {gold_price_text}")
                    browser.close()
                    return None
            else:
                logging.error("Gold price element not found")
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
    price = fetch_gold_price()

    if price:
        save_price(price)

        timestamps, prices = load_history()
        trend = get_trend(prices)

        message = f"💰 Gold Price: ₹{price}\n{trend}"
    else:
        message = "⚠️ Could not fetch today's gold price."

    send_telegram_message(message)

    timestamps, prices = load_history()

    if len(prices) >= 2:
        image_path = generate_plot(timestamps, prices)
        if image_path:
            send_telegram_image(image_path)
    else:
        logging.info("Not enough data for trend graph yet.")