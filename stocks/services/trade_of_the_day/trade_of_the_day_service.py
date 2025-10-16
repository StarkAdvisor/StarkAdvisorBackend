
from stocks.repository.trade_of_the_day_repository import TradeOfTheDayRepository


class TradeOfTheDayService:
      
      def __init__(self, repo: TradeOfTheDayRepository):
        self.repository = repo
      

      def get_trade_of_the_day(self):
        return self.repository.get_most_recent_trade()
  