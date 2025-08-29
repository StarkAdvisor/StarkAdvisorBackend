# stocks/urls.py
from django.urls import path

from stocks.views import TradeOfTheDayView


urlpatterns = [
    path("trade-of-the-day/", TradeOfTheDayView.as_view(), name="trade-of-the-day"),
]
