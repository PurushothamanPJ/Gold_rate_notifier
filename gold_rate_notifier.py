import os
import csv
from datetime import datetime
import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

# --------------------------
# Configuration
# --------------------------
CSV_FILE = "gold_prices.csv"
GRT_URL = "https://www.livechennai.com/gold_silverrate.asp"

# --------------------------
# Scraper (requests + BeautifulSoup)
# --------------------------
def fetch_gold_price():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        response = requests.get(GRT_URL, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        row = soup.select_one("table.today-gold-rate tbody tr")
        gold_price_text = row.find_all("td")[1].text
        gold_price = gold_price_text.replace("₹", "").replace(",", "").split()[0]
        return float(gold_price)

    except Exception as e:
        print(f"⚠️ Could not fetch gold price: {e}")
        return None

# --------------------------
# CSV Handling
# --------------------------
def save_price(price):
    file_exists = os.path.exists(CSV_FILE)
    is_empty = not file_exists or os.path.getsize(CSV_FILE) == 0

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if is_empty:
            writer.writerow(["date", "price"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d"), price])

def load_history():
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        return [], []  # No data yet

    dates, prices = [], []
    with open(CSV_FILE) as f:
        reader = csv.DictReader(f)
        # Check if headers exist
        if reader.fieldnames is None or "date" not in reader.fieldnames or "price" not in reader.fieldnames:
            return [], []  # Invalid or empty CSV
        for row in reader:
            dates.append(row["date"])
            prices.append(float(row["price"]))
    return dates, prices


# --------------------------
# Plotting
# --------------------------
def generate_plot(dates, prices):
    if len(prices) < 2:
        return None  # Not enough data to generate trends

    plt.figure(figsize=(10,5))
    plt.plot(dates, prices, marker='o', linestyle='-', color='gold')
    plt.title("Gold Price History")
    plt.xlabel("Date")
    plt.ylabel("Price (₹ per 1Gm 22K)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    image_path = "gold_price_history.png"
    plt.savefig(image_path)
    plt.close()
    return image_path

# --------------------------
# Telegram
# --------------------------
def send_telegram_message(message: str):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"⚠️ Failed to send message: {e}")

def send_telegram_image(image_path: str):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    files = {"photo": open(image_path, "rb")}
    data = {"chat_id": chat_id}
    try:
        requests.post(url, files=files, data=data)
    except Exception as e:
        print(f"⚠️ Failed to send image: {e}")

# --------------------------
# Main
# --------------------------
if __name__ == "__main__":
    price = fetch_gold_price()
    if price:
        save_price(price)
        message = f"💰 Today's Gold Price: ₹{price}"
    else:
        message = "⚠️ Could not fetch today's gold price."

    send_telegram_message(message)

    # Send plot only if enough historical data
    dates, prices = load_history()
    if len(prices) >= 2:
        image_path = generate_plot(dates, prices)
        if image_path:
            send_telegram_image(image_path)
    else:
        print("Not enough data to generate trends yet. Waiting for more days of data.")
