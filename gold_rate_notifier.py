import os
import random
import csv
from datetime import datetime
import requests
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# --------------------------
# Configuration
# --------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/115.0.1901.188 Safari/537.36",
]

CSV_FILE = "gold_prices.csv"
GRT_URL = "https://www.livechennai.com/gold_silverrate.asp"
TIMEOUT_IN_SECONDS = 10

# --------------------------
# Scraper
# --------------------------
def fetch_gold_price():
    user_agent = random.choice(USER_AGENTS)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f"user-agent={user_agent}")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.set_page_load_timeout(TIMEOUT_IN_SECONDS)
        driver.get(GRT_URL)

        try:
            table_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.today-gold-rate tbody tr"))
            )
            row = table_element
            gold_price_text = row.find_elements(By.TAG_NAME, "td")[1].text
            gold_price = gold_price_text.replace("₹", "").replace(",", "").split()[0]

        except TimeoutException:
            gold_price = None
            print("⚠️ Could not find gold price table.")

    except WebDriverException as e:
        gold_price = None
        print(f"⚠️ WebDriver error: {e}")

    finally:
        driver.quit()

    return gold_price

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
    if not os.path.exists(CSV_FILE):
        return [], []

    dates, prices = [], []
    with open(CSV_FILE) as f:
        reader = csv.DictReader(f)
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
