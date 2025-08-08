import logging
from typing import List

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD

logger = logging.getLogger(__name__)


def add_indicators(df: pd.DataFrame, rsi_period: int = 14, ma_periods: List[int] = [20, 50]) -> pd.DataFrame:
    """
    Add RSI, MACD, and moving averages to DataFrame.

    Parameters:
        df (pd.DataFrame): OHLCV DataFrame.
        rsi_period (int): RSI window (default: 14).
        ma_periods (List[int]): Moving average windows (default: [20, 50]).

    Returns:
        pd.DataFrame: DataFrame with indicators added.
    """
    df = df.copy()

    try:
        # RSI
        df[f"RSI_{rsi_period}"] = RSIIndicator(close=df["Close"], window=rsi_period).rsi()

        # Moving Averages
        for period in ma_periods:
            df[f"MA_{period}"] = df["Close"].rolling(window=period).mean()

        # MACD
        macd = MACD(close=df["Close"], window_fast=12, window_slow=26, window_sign=9)
        df["MACD"] = macd.macd()
        df["MACD_signal"] = macd.macd_signal()
        df["MACD_hist"] = macd.macd_diff()

        # Volume change (optional)
        df["Volume_Change"] = df["Volume"].pct_change().shift(1)

    except Exception as e:
        logger.exception("Error while adding indicators: %s", e)

    # Handle NaNs early (optional — depends on where you drop later)
    df.dropna(inplace=True)

    return df
