import os
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv

# Load secrets from .env
load_dotenv()

# Environment variables you must set in .env:
# TELEGRAM_TOKEN=your bot token from BotFather
# CHAT_ID=your mother's chat id
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def fetch_grt_gold_rate():
    url = "https://www.grtjewels.com/"   # ✅ Yes, include official GRT website
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")

        # find the element with gold price
        gold_button = soup.find("button", {"id": "dropdown-basic-button1"})
        if not gold_button:
            return None

        text = gold_button.get_text(strip=True)

        # extract ₹ number like "₹ 10,190"
        m = re.search(r"₹\s*([\d,]+)", text)
        if not m:
            digits = "".join(ch for ch in text if ch.isdigit())
            return int(digits) if digits else None

        return int(m.group(1).replace(",", ""))

    except Exception as e:
        print(f"Error fetching price: {e}")
        return None


def send_telegram_message(chat_id, token, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print("Telegram message sent ✅")
        return True
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False


def main():
    price = fetch_grt_gold_rate()
    if price is None:
        message = "⚠️ Failed to fetch GRT gold price today."
    else:
        message = f"💰 <b>GRT Gold Rate (22 KT, 1g)</b>\n₹ {price:,}\n\n(Automated daily update)"

    send_telegram_message(CHAT_ID, TELEGRAM_TOKEN, message)


if __name__ == "__main__":
    main()
