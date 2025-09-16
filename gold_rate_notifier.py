import os
import requests
from bs4 import BeautifulSoup

def fetch_gold_price():
    url = "https://www.grtjewels.com"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/"
}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return f"⚠️ Failed to fetch GRT gold price. Error: {e}"

    soup = BeautifulSoup(response.text, "html.parser")
    price_element = soup.find("button", {"id": "dropdown-basic-button1"})
    if not price_element:
        return "⚠️ Could not find gold price on the page."

    return f"💰 Today’s Gold Price: {price_element.text.strip()}"

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
