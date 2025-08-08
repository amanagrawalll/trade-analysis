'''import logging
from typing import Tuple

import pandas as pd

logger = logging.getLogger(__name__)

BUY = 1
SELL = -1
HOLD = 0


def generate_signals(df: pd.DataFrame, rsi_col: str = "RSI_14", ma_short: str = "MA_20", ma_long: str = "MA_50") -> pd.DataFrame:
    """Generate trading signals.

    Buy conditions: RSI < 30 and short MA crossing above long MA.
    Sell conditions: RSI > 70 and short MA crossing below long MA.

    Returns df with `signal` column (1 buy, -1 sell, 0 hold).
    """

    df = df.copy()

    # Crossover signals
    df["ma_diff"] = df[ma_short] - df[ma_long]
    #df["ma_diff_prev"] = df["ma_diff"].shift(1)

    # Conditions
    buy_condition = (df[rsi_col] < 30)  & (df["ma_diff"] > 0)
    sell_condition = (df[rsi_col] > 70)  & (df["ma_diff"] < 0)

    df["signal"] = HOLD
    df.loc[buy_condition, "signal"] = BUY
    df.loc[sell_condition, "signal"] = SELL

    return df


def execute_trade(signals: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
    """Simple backtest executing trades at next day's open price.

    Assumes we can take one position at a time (long only). Returns trades log and total P&L.
    """
    trades = []
    position_open = False
    entry_price = 0.0

    for current_date, row in signals.iterrows():
        signal = row["signal"]
        if signal == BUY and not position_open:
            entry_price = row["Open"]  # enter at open price
            position_open = True
            trades.append({"Date": current_date, "Type": "BUY", "Price": entry_price})
            logger.debug("Entering trade on %s at price %.2f", current_date, entry_price)
        elif signal == SELL and position_open:
            exit_price = row["Open"]
            position_open = False
            pnl = exit_price - entry_price
            trades.append({"Date": current_date, "Type": "SELL", "Price": exit_price, "PnL": pnl})
            logger.debug("Exiting trade on %s at price %.2f, PnL %.2f", current_date, exit_price, pnl)

    # Force close position at the end if still open
    if position_open:
        last_row = signals.iloc[-1]
        exit_price = last_row["Close"]
        pnl = exit_price - entry_price
        trades.append({"Date": signals.index[-1], "Type": "FORCE_SELL", "Price": exit_price, "PnL": pnl})

    trades_df = pd.DataFrame(trades)
    total_pnl = trades_df.get("PnL", pd.Series(dtype=float)).sum()
    return trades_df, total_pnl'''

import logging
from typing import Tuple
import pandas as pd

logger = logging.getLogger(__name__)

# Signal codes
BUY = 1
SELL = -1
HOLD = 0

def generate_signals(df: pd.DataFrame, rsi_col: str = "RSI_14", ma_short: str = "MA_20", ma_long: str = "MA_50") -> pd.DataFrame:
    """
    Generate trading signals using RSI and Moving Average crossover.

    Buy conditions: RSI < 30 AND 20-DMA crosses above 50-DMA (bullish crossover).
    Sell conditions: RSI > 70 AND 20-DMA crosses below 50-DMA (bearish crossover).

    Parameters:
        df (pd.DataFrame): Input OHLCV DataFrame with indicator columns.
        rsi_col (str): Column name for RSI.
        ma_short (str): Column name for 20-DMA.
        ma_long (str): Column name for 50-DMA.

    Returns:
        pd.DataFrame: Copy of input DataFrame with added `signal` column.
    """
    df = df.copy()

    # Moving average difference and crossover detection
    df["ma_diff"] = df[ma_short] - df[ma_long]
    df["ma_diff_prev"] = df["ma_diff"].shift(1)

    ma_crossover_up = (df["ma_diff_prev"] <= 0) & (df["ma_diff"] > 0)
    ma_crossover_down = (df["ma_diff_prev"] >= 0) & (df["ma_diff"] < 0)

    # Buy/sell signal conditions
   
    #buy_condition = df["ma_diff"].gt(0) & df["ma_diff"].shift(1).le(0)  # MA crossover only
    #sell_condition = df["ma_diff"].lt(0) & df["ma_diff"].shift(1).ge(0)
    buy_condition = (df["MACD"] > df["MACD_signal"]) & (df["MACD"].shift(1) <= df["MACD_signal"].shift(1))
    sell_condition = (df["MACD"] < df["MACD_signal"]) & (df["MACD"].shift(1) >= df["MACD_signal"].shift(1))

   

    df["signal"] = HOLD
    df.loc[buy_condition, "signal"] = BUY
    df.loc[sell_condition, "signal"] = SELL

    return df


def execute_trade(signals: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
    """
    Simple long-only backtest executing trades at the next day's open price.

    Assumes:
    - Only one position at a time.
    - Buys on BUY signal, sells on SELL signal.
    - Force-sells at the end if a position is still open.

    Parameters:
        signals (pd.DataFrame): DataFrame with at least "Open", "Close", and "signal" columns.

    Returns:
        Tuple[pd.DataFrame, float]: Trades log DataFrame and total PnL.
    """
    trades = []
    position_open = False
    entry_price = 0.0

    for current_date, row in signals.iterrows():
        signal = row["signal"]

        if signal == BUY and not position_open:
            entry_price = row["Open"]
            position_open = True
            trades.append({"Date": current_date, "Type": "BUY", "Price": entry_price})
            logger.debug("BUY on %s at %.2f", current_date, entry_price)

        elif signal == SELL and position_open:
            exit_price = row["Open"]
            pnl = exit_price - entry_price
            trades.append({"Date": current_date, "Type": "SELL", "Price": exit_price, "PnL": pnl})
            position_open = False
            logger.debug("SELL on %s at %.2f (PnL: %.2f)", current_date, exit_price, pnl)

    # Close any open position at the end of the data
    if position_open:
        last_row = signals.iloc[-1]
        exit_price = last_row["Close"]
        pnl = exit_price - entry_price
        trades.append({"Date": signals.index[-1], "Type": "FORCE_SELL", "Price": exit_price, "PnL": pnl})
        logger.debug("FORCE SELL on %s at %.2f (PnL: %.2f)", signals.index[-1], exit_price, pnl)

    trades_df = pd.DataFrame(trades)
    total_pnl = trades_df.get("PnL", pd.Series(dtype=float)).sum()

    return trades_df, total_pnl

