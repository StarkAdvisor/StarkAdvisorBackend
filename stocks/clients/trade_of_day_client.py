from gradio_client import Client


from stocks.repository.trade_of_the_day_repository import TradeOfTheDayRepository
from stocks.serializers.trade_of_day_serializer import TradeOfTheDaySerializer

class TradeOfTheDayClient:
    @staticmethod
    def fetch_best_trades() -> TradeOfTheDaySerializer:
        client = Client("pschofield2/TradeOfTheDay")
        raw_result = client.predict(api_name="/fetch_best_trades")

        return TradeOfTheDaySerializer.from_raw_text(raw_result)


