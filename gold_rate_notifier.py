import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def fetch_gold_price():
    url = "https://www.grtjewels.com"

    # Configure Selenium Chrome options for headless scraping
    options = Options()
    options.add_argument("--headless")          # Run Chrome in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    # Wait for page to load dynamic content (adjust time if needed)
    time.sleep(5)

    try:
        # Find the gold price element by ID
        price_element = driver.find_element(By.ID, "dropdown-basic-button1")
        gold_price = price_element.text.strip()
    except Exception as e:
        gold_price = f"⚠️ Could not find gold price on the page. Error: {e}"
    finally:
        driver.quit()

    return f"💰 Today’s Gold Price: {gold_price}"

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
