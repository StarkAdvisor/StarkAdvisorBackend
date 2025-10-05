
from datetime import timedelta
from django.utils import timezone

from typing import List, Optional

from django.db.models import Q
from stocks.dataclasses import CurrencyMetricsData, ETFMetricsData, StockMetricsData, TimeSeriesData

from stocks.dtos.dtos import MetricDTO, TimeSeriesDTO
from stocks.dtos.metrics_dto_mapper import MetricsDtoMapper
from stocks.dtos.time_series_dto_mapper import TimeSeriesDTOMapper
from stocks.models import CurrencyMetrics, ETFMetrics, FinancialAsset, StockMetrics, TimeSeries
from django.core.paginator import Paginator






class MarketDataRepository:
    
 

    
    @staticmethod
    def save_time_series(time_series_list: List[TimeSeriesData]):
        """
        Persist a list of TimeSeriesData into the database.
        This uses the same robust conversion logic as before, handling
        possible pd.Series inside each row.
        """
        for ts in time_series_list:
            # Get or create the financial asset
            asset, _ = FinancialAsset.objects.get_or_create(
                ticker=ts.symbol,
                defaults={"name": ts.symbol, "asset_type": ts.asset_type.value}  # store enum value
            )

            # Prepare the data dictionary exactly as before
            TimeSeries.objects.update_or_create(
                asset=asset,
                date=ts.date,
                defaults={
                    "open_price": ts.open_price,
                    "close_price": ts.close_price,
                    "high_price": ts.high_price,
                    "low_price": ts.low_price,
                    "volume": ts.volume
                }
            )

    @staticmethod
    def save_stock_metrics(metrics: StockMetricsData):
        """
        Persist stock metrics into the database.
        """
        # Get or create the financial asset
        asset, _ = FinancialAsset.objects.get_or_create(
            ticker=metrics.symbol,
            defaults={"name": metrics.symbol, "asset_type": "stock"}
        )

        # Prepare metrics dictionary
        metrics_data = {
            "price": metrics.price,
            "daily_change": metrics.daily_change,
            "change_5d_percent": metrics.change_5d_percent,
            "change_1m_percent": metrics.change_1m_percent,
            "change_ytd_percent": metrics.change_ytd_percent,
            "change_5y_percent": metrics.change_5y_percent,
            "high": metrics.high,
            "low": metrics.low,
            "volume": metrics.volume,
            "pe_ratio": metrics.pe_ratio,
            "eps": metrics.eps,
            "dividend_yield": metrics.dividend_yield,
            "market_cap": metrics.market_cap,
            "sector": metrics.sector,
        }

        # Save or update the StockMetrics record
        StockMetrics.objects.update_or_create(
            asset=asset,
            defaults=metrics_data)

    @staticmethod
    def save_etf_metrics(metrics: ETFMetricsData):
        """
        Persist ETF metrics into the database.
        """
        # Get or create the financial asset
        asset, _ = FinancialAsset.objects.get_or_create(
            ticker=metrics.symbol,
            defaults={"name": metrics.symbol, "asset_type": "etf"}
        )

        # Prepare metrics dictionary
        metrics_data = {
            "current_price": metrics.current_price,
            "daily_change_percent": metrics.daily_change_percent,
            "change_5d_percent": metrics.change_5d_percent,
            "change_1m_percent": metrics.change_1m_percent,
            "change_ytd_percent": metrics.change_ytd_percent,
            "change_5y_percent": metrics.change_5y_percent,
            "day_high": metrics.day_high,
            "day_low": metrics.day_low,
            "week52_high": metrics.week52_high,
            "week52_low": metrics.week52_low,
            "volume": metrics.volume,
            "dividend_yield": metrics.dividend_yield,
            "market_cap": metrics.market_cap,
            "nav": metrics.nav,
        }

        # Save or update the ETFMetrics record
        ETFMetrics.objects.update_or_create(
            asset=asset,
            defaults=metrics_data
        )

    @staticmethod
    def save_currency_metrics(metrics: CurrencyMetricsData):
        """
        Persist currency (Forex) metrics into the database.
        """
        # Get or create the financial asset
        asset, _ = FinancialAsset.objects.get_or_create(
            ticker=metrics.symbol,
            defaults={"name": metrics.symbol, "asset_type": "currency"}
        )

        # Prepare metrics dictionary
        metrics_data = {
            "exchange_rate": metrics.exchange_rate,
            "daily_change_percent": metrics.daily_change_percent,
            "change_5d_percent": metrics.change_5d_percent,
            "change_1m_percent": metrics.change_1m_percent,
            "change_ytd_percent": metrics.change_ytd_percent,
            "change_5y_percent": metrics.change_5y_percent,
            "day_high": metrics.day_high,
            "day_low": metrics.day_low,
            "fifty_two_week_high": metrics.fifty_two_week_high,
            "fifty_two_week_low": metrics.fifty_two_week_low,
            "bid": metrics.bid,
            "ask": metrics.ask,
        }

        # Save or update the CurrencyMetrics record
        CurrencyMetrics.objects.update_or_create(
            asset=asset,
            defaults=metrics_data
        )
        
  
    @staticmethod
    def get_stocks_metrics(
        page: int = 1,
        page_size: int = 25,
        sort_by: str = "ticker",
        order: str = "asc",
        query: Optional[str] = None
    ) -> dict:
        """
        Retrieves paginated stock metrics, optionally filtered by a query string (ticker or name).
        """
        queryset = StockMetrics.objects.select_related("asset")

        if query:
            queryset = queryset.filter(
                Q(asset__ticker__istartswith=query) |
                Q(asset__name__istartswith=query)
            )

        sort_field = {
            "ticker": "asset__ticker",
            "price": "price",
            "daily_change": "daily_change"
        }.get(sort_by, "asset__ticker")

        if order == "desc":
            sort_field = f"-{sort_field}"

        queryset = queryset.order_by(sort_field)

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        results = [MetricsDtoMapper.stock_to_dto(m) for m in page_obj]

        return {
            "page": page_obj.number,
            "total_pages": paginator.num_pages,
            "results": results
        }



    @staticmethod
    def get_etfs_metrics(
        sort_by: str = "ticker",
        order: str = "asc",
        query: Optional[str] = None
    ) -> List[MetricDTO]:
        """
        Retrieves all ETF metrics, optionally filtered by query (ticker or name).
        """
        queryset = ETFMetrics.objects.select_related("asset")

        if query:
            queryset = queryset.filter(
                Q(asset__ticker__istartswith=query) |
                Q(asset__name__istartswith=query)
            )


        sort_field = {
            "ticker": "asset__ticker",
            "price": "current_price",
            "daily_change": "daily_change_percent"
        }.get(sort_by, "asset__ticker")

        if order == "desc":
            sort_field = f"-{sort_field}"

        queryset = queryset.order_by(sort_field)
        return [MetricsDtoMapper.etf_to_dto(m) for m in queryset]


    @staticmethod
    def get_currencies_metrics(
        sort_by: str = "ticker",
        order: str = "asc",
        query: Optional[str] = None
    ) -> List[MetricDTO]:
        """
        Retrieves all currency metrics, optionally filtered by query (ticker or name).
        """
        queryset = CurrencyMetrics.objects.select_related("asset")

        if query:
            queryset = queryset.filter(
                Q(asset__ticker__istartswith=query) |
                Q(asset__name__istartswith=query)
            )

        sort_field = {
            "ticker": "asset__ticker",
            "price": "exchange_rate",
            "daily_change": "daily_change_percent"
        }.get(sort_by, "asset__ticker")

        if order == "desc":
            sort_field = f"-{sort_field}"

        queryset = queryset.order_by(sort_field)
        return [MetricsDtoMapper.currency_to_dto(m) for m in queryset]
    
    @staticmethod
    def get_stock_metrics_by_ticker(ticker: str) -> MetricDTO | None:
        try:
            m = StockMetrics.objects.select_related("asset").get(asset__ticker=ticker)
        except StockMetrics.DoesNotExist:
            return None
        return MetricsDtoMapper.stock_to_dto(m)

    @staticmethod
    def get_etf_metrics_by_ticker(ticker: str) -> MetricDTO | None:
        try:
            m = ETFMetrics.objects.select_related("asset").get(asset__ticker=ticker)
        except ETFMetrics.DoesNotExist:
            return None
        return MetricsDtoMapper.etf_to_dto(m)

    @staticmethod
    def get_currency_metrics_by_ticker(ticker: str) -> MetricDTO | None:
        try:
            m = CurrencyMetrics.objects.select_related("asset").get(asset__ticker=ticker)
        except CurrencyMetrics.DoesNotExist:
            return None
        return MetricsDtoMapper.currency_to_dto(m)
    
    @staticmethod
    def get_time_series_from_db(ticker: str, period: str) -> List[TimeSeriesDTO]:
        """
        Retrieves historical time series data (daily granularity) for a given ticker
        and period (5y, 1y, 1m). Data is read directly from the database and mapped
        to DTOs using TimeSeriesDTOMapper.
        """
        valid_periods = {"5y", "1y", "1m"}
        if period not in valid_periods:
            raise ValueError(f"Invalid period '{period}'. Must be one of {valid_periods}.")

        today = timezone.now().date()

        if period == "5y":
            start_date = today - timedelta(days=5 * 365)
        elif period == "1y":
            start_date = today - timedelta(days=365)
        else:  # "1m"
            start_date = today - timedelta(days=30)

        queryset = (
            TimeSeries.objects
            .select_related("asset")
            .filter(asset__ticker=ticker, date__gte=start_date)
            .order_by("date") 
        )

        return TimeSeriesDTOMapper.from_queryset(queryset)


