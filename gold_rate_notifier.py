import os
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# List of common User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/115.0.1901.188 Safari/537.36",
]

def fetch_gold_price():
    url = "https://www.livechennai.com/gold_silverrate.asp"

    # Pick a random User-Agent
    user_agent = random.choice(USER_AGENTS)

    # Configure Selenium Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"user-agent={user_agent}")

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    try:
        # Wait for the gold table to load
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.today-gold-rate tbody tr"))
        )

        # Extract date, 22K gold price, and silver price
        date_text = table.find_element(By.CSS_SELECTOR, "td.date-col").text.strip()
        gold_price_22k = table.find_elements(By.TAG_NAME, "td")[1].text.strip()
        silver_price = table.find_elements(By.TAG_NAME, "td")[2].text.strip()

        message = f"📅 {date_text}\n💰 Gold (22K / 1g): {gold_price_22k}\n🥈 Silver (1g): {silver_price}"

    except Exception as e:
        message = f"⚠️ Could not fetch gold price. Error: {e}"
    finally:
        driver.quit()

    return message

def send_telegram_message(message: str):
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"⚠️ Failed to send message: {e}")

if __name__ == "__main__":
    price_message = fetch_gold_price()
    send_telegram_message(price_message)
