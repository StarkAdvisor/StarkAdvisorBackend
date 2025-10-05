from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class MetricDTO:
    ticker: str
    name: str
    price: Optional[float]
    daily_change: Optional[float]
    extra_metrics: dict



@dataclass
class TimeSeriesDTO:
    ticker: str
    timestamp: datetime  
    close_price: float