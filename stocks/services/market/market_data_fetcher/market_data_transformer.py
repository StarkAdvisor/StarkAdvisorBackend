

import pandas as pd
from typing import Optional

from stocks.dataclasses import AssetType, CurrencyMetricsData, ETFMetricsData, StockMetricsData, TimeSeriesData

class MarketDataTransformer:

    @staticmethod
    def transform_time_series(symbol: str, asset_type: AssetType, raw_data: pd.DataFrame) -> list[TimeSeriesData]:
        """
        Convert raw yfinance DataFrame into a list of TimeSeriesData.
        """
        series = []

        for date, row in raw_data.iterrows():
            ts_data = TimeSeriesData(
                asset_type=asset_type,
                symbol=symbol,
                date=date.to_pydatetime() if hasattr(date, 'to_pydatetime') else date,
                open_price=float(row["Open"].iloc[0]) if isinstance(row["Open"], pd.Series) else float(row["Open"]),
                close_price=float(row["Close"].iloc[0]) if isinstance(row["Close"], pd.Series) else float(row["Close"]),
                high_price=float(row["High"].iloc[0]) if isinstance(row["High"], pd.Series) else float(row["High"]),
                low_price=float(row["Low"].iloc[0]) if isinstance(row["Low"], pd.Series) else float(row["Low"]),
                volume=int(row["Volume"].iloc[0]) if isinstance(row["Volume"], pd.Series) else int(row["Volume"])
            )
            series.append(ts_data)

        return series

    @staticmethod
    def transform_stock_metrics(symbol: str, raw_info: dict, changes: dict) -> StockMetricsData:
        """
        Transform raw yfinance info dict into StockMetricsData with symbol included.
        """
        return StockMetricsData(
            symbol=symbol,
            price=raw_info.get("regularMarketPrice"),
            daily_change=raw_info.get("regularMarketChangePercent"),
            change_5d_percent=changes.get("change_5d_percent"),
            change_1m_percent=changes.get("change_1mo_percent"),
            change_ytd_percent=changes.get("change_ytd_percent"),
            change_5y_percent=changes.get("change_5y_percent"),
            high=raw_info.get("dayHigh"),
            low=raw_info.get("dayLow"),
            volume=raw_info.get("volume"),
            pe_ratio=raw_info.get("trailingPE"),
            eps=raw_info.get("trailingEps"),
            dividend_yield=raw_info.get("dividendYield"),
            market_cap=raw_info.get("marketCap"),
            sector=raw_info.get("sector")
        )

    @staticmethod
    def transform_etf_metrics(symbol: str, raw_info: dict, changes: dict) -> ETFMetricsData:
        """
        Transform raw yfinance ETF info dict into ETFMetricsData with symbol included.
        """
        return ETFMetricsData(
            symbol=symbol,
            current_price=raw_info.get("currentPrice") or raw_info.get("regularMarketPrice"),
            daily_change_percent=raw_info.get("regularMarketChangePercent"),
            change_5d_percent=changes.get("change_5d_percent"),
            change_1m_percent=changes.get("change_1mo_percent"),
            change_ytd_percent=changes.get("change_ytd_percent"),
            change_5y_percent=changes.get("change_5y_percent"),
            day_high=raw_info.get("dayHigh"),
            day_low=raw_info.get("dayLow"),
            week52_high=raw_info.get("fiftyTwoWeekHigh"),
            week52_low=raw_info.get("fiftyTwoWeekLow"),
            volume=raw_info.get("volume"),
            dividend_yield=raw_info.get("dividendYield"),
            market_cap=raw_info.get("marketCap"),
            nav=raw_info.get("navPrice")
        )

    @staticmethod
    def transform_currency_metrics(symbol: str, raw_info: dict, changes: dict, robust_rate: Optional[float]) -> CurrencyMetricsData:
        """
        Transform raw yfinance currency info dict into CurrencyMetricsData with symbol included.
        """
        return CurrencyMetricsData(
            symbol=symbol,
            exchange_rate=robust_rate,
            daily_change_percent=raw_info.get("regularMarketChangePercent"),
            change_5d_percent=changes.get("change_5d_percent"),
            change_1m_percent=changes.get("change_1mo_percent"),
            change_ytd_percent=changes.get("change_ytd_percent"),
            change_5y_percent=changes.get("change_5y_percent"),
            day_high=raw_info.get("dayHigh"),
            day_low=raw_info.get("dayLow"),
            fifty_two_week_high=raw_info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=raw_info.get("fiftyTwoWeekLow"),
            bid=raw_info.get("bid"),
            ask=raw_info.get("ask")
        )
