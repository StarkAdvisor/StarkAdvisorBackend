import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from stocks.models import StockPrice


class YahooFinanceClient:
    

    def get_stock_history(self, ticker, start_date=None, end_date=None):
        if start_date is None:
            start_date = (datetime.today() - timedelta(days=5)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.today().strftime("%Y-%m-%d")

        df = yf.download(ticker, start=start_date, end=end_date)

        if df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df = df.xs(ticker, axis=1, level=1)

        df = df.reset_index()
        df = df.rename(columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })

        return df