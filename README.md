# 💰 Gold Price Notifier

An automated gold price tracking and notification system that scrapes current gold prices, stores historical data, and sends daily updates via Telegram with trend analysis and price history charts.

---

## 🎯 Features

- **Web Scraping**: Automatically fetches the current 22K gold price from GRT Jewels
- **CSV Storage**: Saves all price data with timestamps for historical tracking
- **Trend Analysis**: Identifies whether the price increased, decreased, or remained unchanged
- **Price Visualization**: Generates line charts of price history and sends them via Telegram
- **Automated Scheduling**: Runs daily at 04:30 UTC (10 AM IST) via GitHub Actions
- **Telegram Integration**: Sends real-time price alerts and charts to your Telegram chat
- **Headless Browsing**: Uses Playwright for reliable web scraping without UI overhead

---

## 📋 Project Structure

```
├── gold_rate_notifier.py          # Main scraper script
├── requirements.txt                # Python dependencies
├── gold_prices.csv                 # Historical price data (auto-generated)
├── gold_price_history.png          # Price chart (auto-generated)
├── README.md                        # This file
└── .github/workflows/
    └── scraper.yml                 # GitHub Actions workflow for scheduling
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Telegram Bot Token (from BotFather)
- Telegram Chat ID (where you want to receive messages)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/PurushothamanPJ/Gold_rate_notifier.git
   cd Gold_rate_notifier
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Telegram credentials**
   ```bash
   export TELEGRAM_BOT_TOKEN=your_bot_token
   export TELEGRAM_CHAT_ID=your_chat_id
   ```

4. **Run locally**
   ```bash
   python gold_rate_notifier.py
   ```

---

## 🔧 How It Works

### Main Functions

| Function | Purpose |
|----------|---------|
| `fetch_gold_price()` | Scrapes the 22K gold price from GRT Jewels website |
| `save_price(price)` | Stores price with timestamp in CSV file |
| `load_history()` | Reads historical prices from CSV |
| `get_trend(prices)` | Determines if price went up, down, or stayed same |
| `generate_plot()` | Creates a line chart of price history |
| `send_telegram_message()` | Sends text alerts to Telegram |
| `send_telegram_image()` | Sends price chart images to Telegram |

### Workflow
1. Scrapes the latest gold price from the web
2. Saves it to `gold_prices.csv` with current timestamp
3. Analyzes trend (comparing today vs yesterday)
4. Sends Telegram notification with price and trend
5. If enough data exists (2+ data points), generates and sends a chart

---

## 📦 Dependencies

- **requests**: For making HTTP requests to Telegram API
- **playwright**: For browser automation and web scraping
- **matplotlib**: For generating price history charts

---

## 🤖 GitHub Actions Automation

The project includes a GitHub Actions workflow (`scraper.yml`) that:
- Runs daily at **04:30 UTC** (10 AM IST)
- Sets up Python 3.11 environment
- Installs Chromium and Playwright
- Executes the scraper automatically
- Uses GitHub Secrets for secure credential management

### Setting Up GitHub Actions

1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Add two secrets:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `TELEGRAM_CHAT_ID`: Your Telegram chat ID
3. The workflow will automatically run on schedule or can be triggered manually

---

## 📊 Output

### Telegram Message Example
```
💰 Gold Price: ₹7,300
📈 Increased
```

### CSV Format
```
timestamp,price
2026-04-07 10:30:45,7300.50
2026-04-06 10:30:22,7290.00
```

---

## 🛠️ Configuration

Edit the following in `gold_rate_notifier.py`:
- **CSV_FILE**: Change the file name for storing prices
- **Website URL**: Modify `page.goto()` URL to scrape different sites
- **Price Selector**: Update `page.locator()` if website structure changes
- **Telegram API**: Already configured to use environment variables

---

## 📝 Notes

- Requires internet connection for web scraping and Telegram API calls
- Price data is stored locally in `gold_prices.csv`
- Charts require at least 2 data points to generate
- Playwright automatically handles browser installation via GitHub Actions

---

## 📧 Support

For issues or questions, open an issue on GitHub or check the Telegram logs in GitHub Actions.

---

## 📄 License

MIT License - Feel free to use and modify as needed.