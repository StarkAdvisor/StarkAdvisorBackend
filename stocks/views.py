from django.shortcuts import render

# Create your views here.
# stocks/views/trade_of_the_day_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from stocks.services.trade_of_the_day_service import TradeOfTheDayService
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
