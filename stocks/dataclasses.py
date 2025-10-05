from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List,Optional

class AssetType(Enum):
    STOCK = "stock"
    FOREX = "forex"
    ETF = "etf"


@dataclass
class MarketTicker:
    symbol: str
    name: str


@dataclass
class TimeSeriesData:
    asset_type: AssetType
    symbol: str
    date: datetime
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    volume: float | None = None

@dataclass
class StockMetricsData:
    symbol: str
    price: Optional[float] = None
    daily_change: Optional[float] = None
    change_5d_percent: Optional[float] = None
    change_1m_percent: Optional[float] = None
    change_ytd_percent: Optional[float] = None
    change_5y_percent: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[int] = None
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None
    market_cap: Optional[int] = None
    sector: Optional[str] = None


@dataclass
class ETFMetricsData:
    symbol: str
    current_price: Optional[float] = None
    daily_change_percent: Optional[float] = None
    change_5d_percent: Optional[float] = None
    change_1m_percent: Optional[float] = None
    change_ytd_percent: Optional[float] = None
    change_5y_percent: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    week52_high: Optional[float] = None
    week52_low: Optional[float] = None
    volume: Optional[int] = None
    dividend_yield: Optional[float] = None
    market_cap: Optional[int] = None
    nav: Optional[float] = None


@dataclass
class CurrencyMetricsData:
    symbol: str
    exchange_rate: Optional[float] = None
    daily_change_percent: Optional[float] = None
    change_5d_percent: Optional[float] = None
    change_1m_percent: Optional[float] = None
    change_ytd_percent: Optional[float] = None
    change_5y_percent: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
