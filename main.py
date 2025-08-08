
import argparse
import logging
from typing import List

from algo_trader.data import fetch_data
from algo_trader.backtester import Backtester
from algo_trader.ml_model import train_evaluate
from algo_trader.google_sheets import GoogleSheetsClient
from utils.logger import setup_logger
from algo_trader.telegram_alerts import send_message


DEFAULT_TICKERS: List[str] = [
    # Original three
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    # Additional NIFTY-50 constituents
    "INFY.NS",        # Infosys
    "ITC.NS",         # ITC Ltd.
    "ICICIBANK.NS",   # ICICI Bank
    "SBIN.NS",        # State Bank of India
    "HINDUNILVR.NS",  # Hindustan Unilever
    "BHARTIARTL.NS",  # Bharti Airtel
    "KOTAKBANK.NS",   # Kotak Mahindra Bank
    "AXISBANK.NS",    # Axis Bank
    "LT.NS",          # Larsen & Toubro
    "MARUTI.NS",      # Maruti Suzuki
]

def run_pipeline(tickers: List[str], period_days: int, update_sheets: bool, spreadsheet_name: str | None):
    price_data = fetch_data(tickers, period_days)

    # Backtest
    backtester = Backtester(tickers)
    trades, pnls = backtester.run(price_data)

    # ML evaluation (optional)
    accuracies = train_evaluate(price_data)
    logging.info("ML Accuracies: %s", accuracies)

    # Google Sheets logging
    if update_sheets and spreadsheet_name:
        gclient = GoogleSheetsClient(spreadsheet_name)
        gclient.write_trades_and_summary(trades, pnls)

    # Print summary
    print("Total PnL:", backtester.total_pnl)
    print("Per Ticker PnL:", pnls)
    print("ML Accuracies:", accuracies)

    # Telegram summary
    summary_lines = [
        "*Algo Trading Run Summary*",
        f"Total PnL: {backtester.total_pnl:.2f}",
        "",
        "*Per Ticker PnL*",
    ]
    for t, p in pnls.items():
        summary_lines.append(f"{t}: {float(p):.2f}")
    summary_lines.append("")
    summary_lines.append("*ML Accuracies*")
    for t, acc in accuracies.items():
        summary_lines.append(f"{t}: {acc*100:.1f}%")

    send_message("\n".join(summary_lines))


def parse_args():
    parser = argparse.ArgumentParser(description="Mini Algo Trading Prototype")
    parser.add_argument("--tickers", nargs="*", default=DEFAULT_TICKERS, help="List of ticker symbols")
    parser.add_argument("--period", type=int, default=180, help="Number of days to backtest")
    parser.add_argument("--sheets", action="store_true", help="Enable Google Sheets logging")
    parser.add_argument("--spreadsheet", type=str, help="Google Spreadsheet name")
    return parser.parse_args()


if __name__ == "__main__":
    setup_logger()
    args = parse_args()
    try:
        run_pipeline(args.tickers, args.period, args.sheets, args.spreadsheet)
    except Exception as exc:
        # Send error notification
        send_message(f"⚠️ Algo run failed: {exc}")
        raise
