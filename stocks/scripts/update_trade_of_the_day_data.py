
from starkadvisorbackend.utils.django_setup import ensure_django

# Initialize Django and require the 'stocks' app
ensure_django(require_apps=["stocks"])

from stocks.services.trade_of_the_day.trade_of_the_day_updater import TradeOfTheDayUpdater
from stocks.repository.trade_of_the_day_repository import TradeOfTheDayRepository



if __name__ == "__main__":
    repo = TradeOfTheDayRepository()
    updater = TradeOfTheDayUpdater(repo)
    updater.update_data()
    
