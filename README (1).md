# 📈 Algo Trading Automation – RSI + Moving Average Strategy with ML & Google Sheets Integration

This project is a fully automated mini-algo trading prototype that:
- Fetches historical stock data using `yfinance`
- Applies a rule-based trading strategy (RSI + DMA crossover)
- Backtests trades and computes PnL
- Trains ML models to predict buy/sell signals
- Logs results to Google Sheets
- Sends summary via Telegram alerts

---

## 📌 Features

### ✅ Trading Strategy Logic
- **Buy Signal**: RSI < 30 AND 20-Day MA crosses above 50-Day MA
- **Sell Signal**: RSI > 70 OR 20-Day MA crosses below 50-Day MA
- Executes trades on these signals and logs entry/exit with PnL

### 🤖 Machine Learning Integration
- Predicts future buy/sell signals based on technical indicators
- Models used:
  - Logistic Regression
  - Decision Tree
  - Random Forest
  - XGBoost
  - LightGBM
  - Stacking Classifier
- Displays per-ticker accuracy after evaluation

### 📊 Google Sheets Automation
- Pushes PnL and trade logs to a Google Sheet:
  - `Summary_PnL`: Per-ticker total returns
  - `Trades_<Ticker>`: All trades with dates, prices, PnL

### 🔔 Telegram Alerts
- Sends summary (PnL + ML accuracy) or failure notifications via Telegram

---

## 🛠️ Project Structure

```bash
.
├── algo_trader/
│   ├── backtester.py         # Executes trades based on strategy
│   ├── data.py               # Fetches historical stock data
│   ├── indicators.py         # Computes RSI, MAs, etc.
│   ├── ml_model.py           # ML training and evaluation logic
│   ├── google_sheets.py      # Google Sheets integration
│   ├── telegram_alerts.py    # Telegram bot messaging
│
├── utils/
│   └── logger.py             # Logging setup
│
├── main.py                   # Pipeline entry point
├── requirements.txt          # Python dependencies
└── README.md                 # You're here!
```

---

## 🚀 How to Run

### 🔧 1. Install Requirements

```bash
pip install -r requirements.txt
```

### 🔐 2. Setup Google Sheets Access
- Create a Google Service Account
- Share your spreadsheet with the service account email
- Place the `.json` credentials file in the root directory
- Set the environment variable in `.env`:
```env
GOOGLE_APPLICATION_CREDENTIALS=your_credentials.json
```

### 💬 3. Setup Telegram Alerts (Optional)
- Create a Telegram bot using [@BotFather](https://t.me/botfather)
- Get your `BOT_TOKEN` and chat ID
- Add to `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### ▶️ 4. Run the Algo

```bash
python main.py --period 180 --sheets --spreadsheet "My Algo Trade Log"
```

#### Args:
- `--period`: Backtest period in days (default: 180)
- `--sheets`: Enable Google Sheets logging
- `--spreadsheet`: Spreadsheet name to log trades

---

## ✅ Sample Output

```
Total PnL: 918.50
Per Ticker PnL:
  RELIANCE.NS: ₹42.90
  TCS.NS: ₹-9.57
  ...
ML Accuracies:
  RELIANCE.NS: 45.5%
  TCS.NS: 54.5%
  ...
```

Sheets will be updated like:

| Ticker       | Total PnL |
|--------------|-----------|
| RELIANCE.NS  | ₹42.90    |
| MARUTI.NS    | ₹517.43   |

---

## 🎓 Concepts Used

- Technical Indicators: RSI, Moving Averages, MACD
- Supervised ML Classification
- Model Evaluation: Accuracy Scores
- Data Fetching via `yfinance`
- Logging with `logging`
- Automation via `gspread`, `gspread-dataframe`
- Alerts via Telegram Bot API

---


## ✅ Final Checklist

- [x] Trading logic implemented and backtested
- [x] ML predictions integrated and evaluated
- [x] Google Sheets logging working
- [x] Telegram alerts implemented
- [x] All modular code with logging
- [x] Requirements.txt updated
- [x] README & videos prepared