


from stocks.dtos.dtos import MetricDTO


class MetricsDtoMapper:

    @staticmethod
    def safe_float(value):
        """
        Converts a value to float safely.
        Returns None if the value is NaN, infinite, or None.
        """
        import math
        if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
            return None
        return float(value)

    

    @staticmethod
    def stock_to_dto(m) -> MetricDTO:
        return MetricDTO(
            ticker=m.asset.ticker,
            name=m.asset.name,
            price=MetricsDtoMapper.safe_float(m.price),
            daily_change=MetricsDtoMapper.safe_float(m.daily_change),
            extra_metrics={
                "change_5d_percent": MetricsDtoMapper.safe_float(m.change_5d_percent),
                "change_1m_percent": MetricsDtoMapper.safe_float(m.change_1m_percent),
                "change_ytd_percent": MetricsDtoMapper.safe_float(m.change_ytd_percent),
                "change_5y_percent": MetricsDtoMapper.safe_float(m.change_5y_percent),
                "high": MetricsDtoMapper.safe_float(m.high),
                "low": MetricsDtoMapper.safe_float(m.low),
                "volume": MetricsDtoMapper.safe_float(m.volume),
                "pe_ratio": MetricsDtoMapper.safe_float(m.pe_ratio),
                "eps": MetricsDtoMapper.safe_float(m.eps),
                "dividend_yield": MetricsDtoMapper.safe_float(m.dividend_yield),
                "market_cap": MetricsDtoMapper.safe_float(m.market_cap),
                "sector": m.sector,
            }
        )
        
        
    

    @staticmethod
    def etf_to_dto(m) -> MetricDTO:
        return MetricDTO(
            ticker=m.asset.ticker,
            name=m.asset.name,
            price=MetricsDtoMapper.safe_float(m.current_price),
            daily_change=MetricsDtoMapper.safe_float(m.daily_change_percent),
            extra_metrics={
                "change_5d_percent": MetricsDtoMapper.safe_float(m.change_5d_percent),
                "change_1m_percent": MetricsDtoMapper.safe_float(m.change_1m_percent),
                "change_ytd_percent": MetricsDtoMapper.safe_float(m.change_ytd_percent),
                "change_5y_percent": MetricsDtoMapper.safe_float(m.change_5y_percent),
                "day_high": MetricsDtoMapper.safe_float(m.day_high),
                "day_low": MetricsDtoMapper.safe_float(m.day_low),
                "week52_high": MetricsDtoMapper.safe_float(m.week52_high),
                "week52_low": MetricsDtoMapper.safe_float(m.week52_low),
                "volume": MetricsDtoMapper.safe_float(m.volume),
                "dividend_yield": MetricsDtoMapper.safe_float(m.dividend_yield),
                "market_cap": MetricsDtoMapper.safe_float(m.market_cap),
                "nav": MetricsDtoMapper.safe_float(m.nav),
            }
        )

    @staticmethod
    def currency_to_dto(m) -> MetricDTO:
        return MetricDTO(
            ticker=m.asset.ticker,
            name=m.asset.name,
            price=MetricsDtoMapper.safe_float(m.exchange_rate),
            daily_change=MetricsDtoMapper.safe_float(m.daily_change_percent),
            extra_metrics={
                "change_5d_percent": MetricsDtoMapper.safe_float(m.change_5d_percent),
                "change_1m_percent": MetricsDtoMapper.safe_float(m.change_1m_percent),
                "change_ytd_percent": MetricsDtoMapper.safe_float(m.change_ytd_percent),
                "change_5y_percent": MetricsDtoMapper.safe_float(m.change_5y_percent),
                "day_high": MetricsDtoMapper.safe_float(m.day_high),
                "day_low": MetricsDtoMapper.safe_float(m.day_low),
                "fifty_two_week_high": MetricsDtoMapper.safe_float(m.fifty_two_week_high),
                "fifty_two_week_low": MetricsDtoMapper.safe_float(m.fifty_two_week_low),
                "bid": MetricsDtoMapper.safe_float(m.bid),
                "ask": MetricsDtoMapper.safe_float(m.ask),
            }
        )
