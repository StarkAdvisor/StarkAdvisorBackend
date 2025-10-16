from django.shortcuts import render

# Create your views here.
# stocks/views/trade_of_the_day_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from stocks.dataclasses import AssetType
from stocks.dtos.time_series_dto_mapper import TimeSeriesDTOMapper
from stocks.serializers.metric_dto_serializer import MetricDTOSerializer
from stocks.serializers.time_series_dto_serializer import TimeSeriesDTOSerializer
from stocks.services.market.market_data_fetcher.market_data_fetcher import MarketDataFetcher
from stocks.services.market.market_data_repository.market_data_repository import MarketDataRepository
from stocks.services.trade_of_the_day.trade_of_the_day_service import TradeOfTheDayService
from stocks.repository.trade_of_the_day_repository import TradeOfTheDayRepository


class TradeOfTheDayView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        repo = TradeOfTheDayRepository()
        self.service = TradeOfTheDayService(repo)

    def get(self, request):
        try:
            trades = self.service.get_trade_of_the_day()
            return Response(trades, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StockMetricsView(APIView):
    """
    Endpoint to obtain stock metrics (StockMetrics) with pagination, sorting, and optional search.
    """
    def get(self, request):
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 25))
        sort_by = request.GET.get("sort_by", "ticker")
        order = request.GET.get("order", "asc")
        query = request.GET.get("query", None)  # 🔍 Nuevo parámetro de búsqueda

        data = MarketDataRepository.get_stocks_metrics(page, page_size, sort_by, order, query)

        serializer = MetricDTOSerializer(data["results"], many=True)
        return Response({
            "page": data["page"],
            "total_pages": data["total_pages"],
            "results": serializer.data
        }, status=status.HTTP_200_OK)


class ETFMetricsView(APIView):
    """
    Endpoint for obtaining sorted ETF metrics, with optional search.
    """
    def get(self, request):
        sort_by = request.GET.get("sort_by", "ticker")
        order = request.GET.get("order", "asc")
        query = request.GET.get("query", None)  # 🔍 Nuevo parámetro de búsqueda

        results = MarketDataRepository.get_etfs_metrics(sort_by, order, query)
        serializer = MetricDTOSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class CurrencyMetricsView(APIView):
    """
    Endpoint for obtaining currency metrics (Forex) with sorting and optional search.
    """
    def get(self, request):
        sort_by = request.GET.get("sort_by", "ticker")
        order = request.GET.get("order", "asc")
        query = request.GET.get("query", None)  # 🔍 Nuevo parámetro de búsqueda

        results = MarketDataRepository.get_currencies_metrics(sort_by, order, query)
        serializer = MetricDTOSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class StockMetricDetailView(APIView):
    """
    Endpoint: /api/metrics/stocks/<ticker>/
    Obtiene las métricas de un stock específico por su ticker.
    """
    def get(self, request, ticker: str):
        dto = MarketDataRepository.get_stock_metrics_by_ticker(ticker)
        if dto is None:
            return Response({"detail": f"No se encontraron métricas para el ticker '{ticker}'."},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(dto.__dict__, status=status.HTTP_200_OK)


class ETFMetricDetailView(APIView):
    """
    Endpoint: /api/metrics/etfs/<ticker>/
    Obtiene las métricas de un ETF específico por su ticker.
    """
    def get(self, request, ticker: str):
        dto = MarketDataRepository.get_etf_metrics_by_ticker(ticker)
        if dto is None:
            return Response({"detail": f"No se encontraron métricas para el ETF '{ticker}'."},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(dto.__dict__, status=status.HTTP_200_OK)


class CurrencyMetricDetailView(APIView):
    """
    Endpoint: /api/metrics/currencies/<ticker>/
    Obtiene las métricas de una divisa específica por su ticker.
    """
    def get(self, request, ticker: str):
        dto = MarketDataRepository.get_currency_metrics_by_ticker(ticker)
        if dto is None:
            return Response({"detail": f"No se encontraron métricas para la divisa '{ticker}'."},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(dto.__dict__, status=status.HTTP_200_OK)



class TimeSeriesView(APIView):
    """
    Endpoint to retrieve a time series for a given ticker and period.
    - Uses SQL data for (5y, 1y, 1m) with daily granularity.
    - Uses Yahoo Finance for (5d, 1d) with hourly granularity.
    """

    def get(self, request):
        ticker = request.GET.get("ticker")
        period = request.GET.get("period", "1y")  # default: 1 year
        asset_type = request.GET.get("asset_type", "stock").upper()

        # 🔎 Validate input
        if not ticker:
            return Response({"error": "Missing 'ticker' parameter."}, status=status.HTTP_400_BAD_REQUEST)

        valid_periods = {"5y", "1y", "1m", "5d", "1d"}
        if period not in valid_periods:
            return Response({"error": f"Invalid period '{period}'. Must be one of {valid_periods}."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # 🧭 Determine source of data based on period
            if period in {"5y", "1y", "1m"}:
                # From SQL database (daily granularity)
                data = MarketDataRepository.get_time_series_from_db(ticker, period)

            else:
                # From Yahoo Finance (hourly or 4h granularity)
                interval = "15m" if period == "1d" else "1h"
                data = MarketDataFetcher.get_time_series(
                    ticker=ticker,
                    asset_type=AssetType[asset_type],
                    period=period,
                    interval=interval
                )
                data = TimeSeriesDTOMapper.timedata_to_dto(data)
                
            # 🧱 Serialize result
            serializer = TimeSeriesDTOSerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)