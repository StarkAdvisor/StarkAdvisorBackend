
import os
import django
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from decimal import Decimal, InvalidOperation

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "starkadvisorbackend.settings") 
django.setup()

from stocks.repository.stock_repository import StockRepository
from stocks.service.stock_data_fetcher import StockDataFetcher
from stocks.models import StockPrice

class StockUpdater:
    def __init__(self, fetcher: StockDataFetcher, repo: StockRepository):
        self.fetcher = fetcher
        self.repo = repo

    def fetch_and_store(self, tickers, start_date=None, end_date=None):
        for ticker in tickers:
            df = self.fetcher.fetch(ticker, start_date, end_date)
            if df is None:
                continue
            for _, row in df.iterrows():
                self.repo.save_stock_price(ticker, row)
            print(f"✅ Saved {ticker} data from {start_date} to {end_date}")


if __name__ == "__main__":
    # universo inicial
    universe = ["AAPL", "MSFT", "GOOGL", "AMZN", "SPY"]
    stock_fetcher = StockDataFetcher()
    stock_repo = StockRepository()
    stock_updater = StockUpdater(stock_fetcher, stock_repo)
    # ejemplo: traer últimos 5 años
    start_date = (datetime.today() - timedelta(days=5*365)).strftime('%Y-%m-%d')
    stock_updater.fetch_and_store(universe, start_date=start_date)

