import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from stocks.models import StockPrice


class StockRepository:
    
    def save_stock_price(self, ticker, row):
        StockPrice.objects.update_or_create(
            ticker=ticker,
            date=row["date"],
            defaults={
                "open": StockRepository._safe_decimal(row["open"]),
                "high": StockRepository._safe_decimal(row["high"]),
                "low": StockRepository._safe_decimal(row["low"]),
                "close": StockRepository._safe_decimal(row["close"]),
                "volume": int(row["volume"]) if not pd.isna(row["volume"]) else 0,
            }
        )

    def _safe_decimal( value):
        try:
            if pd.isna(value):
                return None
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None