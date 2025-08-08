import logging
from typing import Tuple
import pandas as pd

logger = logging.getLogger(__name__)

# Signal codes
BUY = 1
SELL = -1
HOLD = 0

def generate_signals(df: pd.DataFrame, rsi_col: str = "RSI_14", ma_short: str = "MA_20", ma_long: str = "MA_50") -> pd.DataFrame:
  
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


