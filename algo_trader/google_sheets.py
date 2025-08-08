"""Google Sheets integration utility."""
import logging
import os
from typing import Dict

import pandas as pd
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import gspread

logger = logging.getLogger(__name__)

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]


class GoogleSheetsClient:
    def __init__(self, spreadsheet_name: str):
        credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        if not credentials_path or not os.path.exists(credentials_path):
            raise FileNotFoundError("Google service account credentials not found. Set GOOGLE_SERVICE_ACCOUNT_FILE env variable.")
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, SCOPES)
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open(spreadsheet_name)
        logger.info("Connected to Google Sheets: %s", spreadsheet_name)

    def write_df(self, df: pd.DataFrame, worksheet_name: str):
        try:
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
                worksheet.clear()
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")
            set_with_dataframe(worksheet, df, include_index=True, include_column_header=True, resize=True)
            logger.info("Wrote %d rows to sheet %s", len(df), worksheet_name)
        except Exception as exc:
            logger.exception("Failed to write to Google Sheet %s: %s", worksheet_name, exc)

    def write_trades_and_summary(self, trades: Dict[str, pd.DataFrame], pnls: Dict[str, float]):
        summary_df = pd.DataFrame({"Ticker": list(pnls.keys()), "PnL": list(pnls.values())})
        win_ratio = (summary_df["PnL"] > 0).mean()
        summary_df.loc[len(summary_df.index)] = ["TOTAL", summary_df["PnL"].sum()]
        summary_df.loc[len(summary_df.index)] = ["Win_Ratio", win_ratio]

        self.write_df(summary_df, "Summary_PnL")
        for ticker, df in trades.items():

            self.write_df(df, f"Trades_{ticker}")
