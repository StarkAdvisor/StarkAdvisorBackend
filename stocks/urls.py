# stocks/urls.py
from django.urls import path

from stocks.views import CurrencyMetricDetailView, CurrencyMetricsView, ETFMetricDetailView, ETFMetricsView, StockMetricDetailView, StockMetricsView, TimeSeriesView, TradeOfTheDayView


urlpatterns = [
    path("trade-of-the-day/", TradeOfTheDayView.as_view(), name="trade-of-the-day"),
    path("metrics/stocks/", StockMetricsView.as_view(), name="stock-metrics"),
    path("metrics/etfs/", ETFMetricsView.as_view(), name="etf-metrics"),
    path("metrics/currencies/", CurrencyMetricsView.as_view(), name="currency-metrics"),
    
    path("metrics/stocks/<str:ticker>/", StockMetricDetailView.as_view(), name="stock-metric-detail"),
    path("metrics/etfs/<str:ticker>/", ETFMetricDetailView.as_view(), name="etf-metric-detail"),
    path("metrics/currencies/<str:ticker>/", CurrencyMetricDetailView.as_view(), name="currency-metric-detail"),
    path("metrics/time-series/", TimeSeriesView.as_view(), name="time-series"),
]
