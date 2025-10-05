
from typing import List
import requests
import pandas as pd
from io import StringIO

from stocks.dataclasses import MarketTicker

class MarketTickerProvider:
    @staticmethod
    def get_sp500_tickers() -> List[MarketTicker]:
        """
        Retrieve tickers and company names for all S&P 500 components from Wikipedia.
        """
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/140.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(url, headers=headers)
        sp500_table = pd.read_html(StringIO(response.text))[0]

        tickers = [t.replace('.', '-') for t in sp500_table['Symbol'].tolist()]
        names = sp500_table['Security'].tolist()

        tickers_data = [MarketTicker(symbol=t, name=n) for t, n in zip(tickers, names)]

        print(f"✅ Found {len(tickers_data)} S&P 500 tickers from Wikipedia")

        return tickers_data

    @staticmethod
    def get_etf_tickers() -> List[MarketTicker]:
        """
        Retrieve a predefined list of popular ETF tickers and their names.
        """
        etfs = {
            "SPY": "S&P 500 ETF",
            "VOO": "Vanguard S&P 500 ETF",
            "QQQ": "Nasdaq 100 ETF",
            "DIA": "Dow Jones Industrial Average ETF",
            "IWM": "Russell 2000 ETF",
            "EFA": "MSCI EAFE ETF",
            "EEM": "Emerging Markets ETF",
            "XLF": "Financials Select Sector ETF",
            "XLK": "Technology Select Sector ETF",
            "XLE": "Energy Select Sector ETF",
            "XLV": "Health Care Select Sector ETF",
            "GLD": "Gold ETF",
            "SLV": "Silver ETF",
            "ARKK": "ARK Innovation ETF",
            "VTI": "Vanguard Total Stock Market ETF",
        }

        tickers_data = [MarketTicker(symbol=symbol, name=name) for symbol, name in etfs.items()]

        print(f"✅ Found {len(tickers_data)} ETFs in the predefined pool")

        return tickers_data

    @staticmethod
    def get_currency_tickers() -> List[MarketTicker]:
        """
        Retrieve a predefined list of major and popular Forex currency pairs.
        """
        currencies = {
            # Major pairs
            "EURUSD=X": "Euro / US Dollar",
            "USDJPY=X": "US Dollar / Japanese Yen",
            "GBPUSD=X": "British Pound / US Dollar",
            "USDCHF=X": "US Dollar / Swiss Franc",
            "AUDUSD=X": "Australian Dollar / US Dollar",
            "USDCAD=X": "US Dollar / Canadian Dollar",
            "NZDUSD=X": "New Zealand Dollar / US Dollar",

            # Popular crosses
            "EURGBP=X": "Euro / British Pound",
            "EURJPY=X": "Euro / Japanese Yen",
            "GBPJPY=X": "British Pound / Japanese Yen",
        }

        tickers_data = [MarketTicker(symbol=symbol, name=name) for symbol, name in currencies.items()]

        print(f"✅ Found {len(tickers_data)} currency pairs in the predefined pool")

        return tickers_data
