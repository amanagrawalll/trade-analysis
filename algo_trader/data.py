import logging
from datetime import datetime, timedelta
from typing import List, Dict

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

DEFAULT_PERIOD_DAYS = 365  # 1 year


def normalize_ticker(ticker: str) -> str:
    """Ensure .NS is appended for NSE tickers."""
    return ticker if ticker.endswith(".NS") else f"{ticker}.NS"


def fetch_data(tickers: List[str], period_days: int = DEFAULT_PERIOD_DAYS, interval: str = "1d") -> Dict[str, pd.DataFrame]:
    """
    Fetch historical stock data for given tickers using yfinance.

    Parameters:
        tickers (List[str]): Ticker symbols (NSE should end with .NS).
        period_days (int): Number of past days to retrieve. Default = 365.
        interval (str): Interval string for data (e.g., "1d", "1h"). Default = "1d".

    Returns:
        Dict[str, pd.DataFrame]: Mapping from ticker to OHLCV DataFrame.
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=period_days)

    logger.info("Fetching data for tickers %s from %s to %s", tickers, start_date.date(), end_date.date())
    all_data: Dict[str, pd.DataFrame] = {}

    for raw_ticker in tickers:
        ticker = normalize_ticker(raw_ticker)
        df = pd.DataFrame()

        for attempt in range(3):
            try:
                df = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
                if not df.empty:
                    break
                logger.warning("Empty data for %s (attempt %d)", ticker, attempt + 1)
            except Exception as exc:
                logger.warning("Attempt %d failed for %s: %s", attempt + 1, ticker, exc)

        if df.empty:
            logger.error("Failed to fetch data for %s after 3 attempts.", ticker)
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(-1)

        df.dropna(how="all", inplace=True)
        df.index = pd.to_datetime(df.index)

        all_data[ticker] = df
        logger.info("Fetched %d rows for %s", len(df), ticker)

    if not all_data:
        raise ValueError("No data fetched for any ticker.")

    return all_data
