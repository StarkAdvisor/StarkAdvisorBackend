
import os
import django

from stocks.services.trade_of_the_day.trade_of_the_day_updater import TradeOfTheDayUpdater
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "starkadvisorbackend.settings") 
django.setup()

from stocks.repository.trade_of_the_day_repository import TradeOfTheDayRepository



if __name__ == "__main__":
    repo = TradeOfTheDayRepository()
    updater = TradeOfTheDayUpdater(repo)
    updater.update_data()
    
