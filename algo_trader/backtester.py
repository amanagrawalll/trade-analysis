import logging
from typing import Dict, List, Tuple

import pandas as pd

from .indicators import add_indicators
from .strategy import generate_signals, execute_trade

logger = logging.getLogger(__name__)


class Backtester:
    """Backtest trading strategy for multiple tickers."""

    def __init__(self, tickers: List[str]):
        self.tickers = tickers
        self.trades: Dict[str, pd.DataFrame] = {}
        self.pnls: Dict[str, float] = {}

    def run(self, price_data: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, float]]:
        """
        Run backtest for each ticker.

        Parameters:
            price_data (Dict[str, pd.DataFrame]): Mapping of ticker to its OHLCV data.

        Returns:
            Tuple containing:
                - trades (Dict[str, pd.DataFrame]): Trade logs per ticker.
                - pnls (Dict[str, float]): PnL per ticker.
        """
        for ticker, df in price_data.items():
            if df.empty or len(df) < 60:
                logger.warning("Skipping %s due to insufficient data (%d rows)", ticker, len(df))
                continue

            logger.info("Backtesting %s", ticker)
            df_ind = add_indicators(df)
            df_signal = generate_signals(df_ind)
            trades_df, pnl = execute_trade(df_signal)

            self.trades[ticker] = trades_df
            self.pnls[ticker] = pnl

            logger.info("Executed %d trades for %s", len(trades_df), ticker)
            logger.info("Total PnL for %s: %.2f", ticker, pnl)

        return self.trades, self.pnls

    @property
    def total_pnl(self) -> float:
        """Calculate total portfolio PnL across all tickers."""
        return sum(self.pnls.values())

    def to_dataframe(self) -> pd.DataFrame:
        """
        Combine all trades into a single DataFrame.

        Returns:
            pd.DataFrame: All trades across tickers with 'Ticker' column.
        """
        all_trades = []
        for ticker, trades_df in self.trades.items():
            df = trades_df.copy()
            df["Ticker"] = ticker
            all_trades.append(df)
        return pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
