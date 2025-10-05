
from stocks.clients.trade_of_day_client import TradeOfTheDayClient
from stocks.repository.trade_of_the_day_repository import TradeOfTheDayRepository


class TradeOfTheDayUpdater:
    def __init__(self, repo: TradeOfTheDayRepository):
        self.repo = repo

    def update_data(self):
        result = TradeOfTheDayClient.fetch_best_trades()
        self.repo.save_trades([trade.model_dump() for trade in result])

