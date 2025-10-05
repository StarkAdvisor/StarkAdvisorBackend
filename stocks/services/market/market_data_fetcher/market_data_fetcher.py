from typing import List
import yfinance as yf
from datetime import datetime

import pandas as pd

from stocks.dataclasses import AssetType, CurrencyMetricsData, ETFMetricsData, StockMetricsData, TimeSeriesData
from stocks.services.market.market_data_fetcher.market_data_transformer import MarketDataTransformer
class MarketDataFetcher:

    @staticmethod
    def get_time_series(
        ticker: str,
        asset_type: AssetType,
        period: str = "5y",
        interval: str = "1d"
    ) -> list[TimeSeriesData]:
        """
        Download the time series of a financial asset and return it as a list of TimeSeriesData.
        Delegates the row-to-dataclass transformation to MarketDataTransformer.

        :param ticker: Asset symbol (e.g., AAPL, EURUSD=X)
        :param asset_type: Type of asset (AssetType.STOCK, AssetType.ETF, AssetType.FOREX)
        :param period: Data period (e.g., 1d, 5d, 1mo, 6mo, 1y, 5y, max)
        :param interval: Data interval (e.g., 1m, 5m, 15m, 1h, 1d, 1wk, 1mo)
        :return: List of TimeSeriesData
        """
        
        try:
            raw_data = yf.download(ticker, period=period, interval=interval, auto_adjust=False)

            if raw_data.empty:
                return []

            return MarketDataTransformer.transform_time_series(
                symbol=ticker,
                asset_type=asset_type,
                raw_data=raw_data
            )

        except Exception as e:
            raise RuntimeError(f"Error downloading time series for {ticker}: {e}")

    @staticmethod
    def get_stock_metrics(ticker: str) -> StockMetricsData:

        """
        Fetch the latest stock metrics for a given ticker and return as a StockMetricsData object.
        Calculates historical percentage changes (5d, 1mo, YTD, 5y) based on historical closing prices.
        :param ticker: Stock symbol (e.g., AAPL)
        :return: StockMetricsData object with the metrics
        """
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            if not info:
                return StockMetricsData(symbol=ticker)

            periods = ["5d", "1mo", "ytd", "5y"]
            changes = {}

            for period in periods:
                try:
                    hist = stock.history(period=period, interval="1d")
                    if not hist.empty:
                        first_close = hist["Close"].iloc[0]
                        last_close = hist["Close"].iloc[-1]
                        changes[f"change_{period}_percent"] = ((last_close - first_close) / first_close) * 100
                except Exception:
                    changes[f"change_{period}_percent"] = None

            return MarketDataTransformer.transform_stock_metrics(
                symbol=ticker,
                raw_info=info,
                changes=changes
            )

        except Exception as e:
            raise RuntimeError(f"Error fetching stock metrics for {ticker}: {e}")

    @staticmethod
    def get_etf_metrics(ticker: str) -> ETFMetricsData:
        
        """
        Fetch the latest ETF metrics for a given ticker and return as an ETFMetricsData object.
        Calculates historical percentage changes (5d, 1mo, YTD, 5y) based on historical closing prices.
        :param ticker: ETF symbol (e.g., SPY)
        :return: ETFMetricsData object with the metrics
        """
        
        try:
            etf = yf.Ticker(ticker)
            info = etf.info

            if not info:
                return ETFMetricsData(symbol=ticker)

            periods = ["5d", "1mo", "ytd", "5y"]
            changes = {}

            for period in periods:
                try:
                    hist = etf.history(period=period, interval="1d")
                    if not hist.empty:
                        first_close = hist["Close"].iloc[0]
                        last_close = hist["Close"].iloc[-1]
                        changes[f"change_{period}_percent"] = ((last_close - first_close) / first_close) * 100
                except Exception:
                    changes[f"change_{period}_percent"] = None

            return MarketDataTransformer.transform_etf_metrics(
                symbol=ticker,
                raw_info=info,
                changes=changes
            )

        except Exception as e:
            raise RuntimeError(f"Error fetching ETF metrics for {ticker}: {e}")

    @staticmethod
    def get_currency_metrics(ticker: str) -> CurrencyMetricsData:
        
        
        """
        Fetch the latest Forex metrics for a given currency ticker and return as a CurrencyMetricsData object.
        Calculates historical percentage changes (5d, 1mo, YTD, 5y) based on historical closing prices.
        :param ticker: Currency symbol (e.g., "EURUSD=X")
        :return: CurrencyMetricsData object with the metrics
        """
        
        try:
            fx = yf.Ticker(ticker)
            info = fx.info

            if not info:
                return CurrencyMetricsData(symbol=ticker)

            robust_rate = info.get("currentPrice") or info.get("regularMarketPrice")
            if not robust_rate:
                hist = fx.history(period="1d", interval="1d")
                if not hist.empty:
                    robust_rate = hist["Close"].iloc[-1]

            periods = ["5d", "1mo", "ytd", "5y"]
            changes = {}

            for period in periods:
                try:
                    hist = fx.history(period=period, interval="1d")
                    if not hist.empty:
                        first_close = hist["Close"].iloc[0]
                        last_close = hist["Close"].iloc[-1]
                        changes[f"change_{period}_percent"] = ((last_close - first_close) / first_close) * 100
                except Exception:
                    changes[f"change_{period}_percent"] = None

            return MarketDataTransformer.transform_currency_metrics(
                symbol=ticker,
                raw_info=info,
                changes=changes,
                robust_rate=robust_rate
            )

        except Exception as e:
            raise RuntimeError(f"Error fetching currency metrics for {ticker}: {e}")
