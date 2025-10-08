from starkadvisorbackend.utils.django_setup import ensure_django

# Initialize Django and require the 'news' app
ensure_django(require_apps=["news"])
import time
from datetime import datetime, timedelta

from news.repository.repository import NewsRepository
from news.services.news_service import NewsService




# lista de categorías que definimos antes
topics = [
    "Stock Market", "Interest Rates", "Federal Reserve Policies", "S&P 500",
    "Banking Sector", "Mutual Funds & ETFs", "Corporate Earnings",
    "US Economy & Inflation", "Budget & Fiscal Policies", "Tech Sector",
    "Energy Sector", "Healthcare & Pharma", "Consumer Goods",
    "Apple", "Microsoft", "Amazon", "Alphabet", "Meta",
    "Tesla", "NVIDIA"
]

MAX_ARTICLES = 100
MAX_RETRIES = 3
service = NewsService()
repository = NewsRepository()

def get_last_scraped_date():
    metadata = repository.get_metadata("last_scraped_date")
    if metadata:
        return metadata
    return datetime.now() - timedelta(days=90)  # default: ultimo ano

def update_last_scraped_date(date: datetime):
    repository.update_metadata("last_scraped_date", date)

def run_scraper():
    last_scraped = get_last_scraped_date()
    today = datetime.now()

    for category in topics:
        print(f"\n Scraping categoría: {category}")

        retries = 0
        articles = []
        while retries < MAX_RETRIES and not articles:
            articles = service.get_news_with_sentiment(
                category,
                start_date=last_scraped + timedelta(days=1),
                end_date=today,
                max_articles=MAX_ARTICLES
            )
            if not articles:
                retries += 1
                print(f" No se encontraron artículos. Reintento {retries}/{MAX_RETRIES}")
                time.sleep(7)  # espera entre intentos

        if articles:
            print(f" Guardando {len(articles)} artículos en DB para {category}")
            service.save_scraped_news(articles)
        else:
            print(f" No se pudo obtener artículos para {category} después de {MAX_RETRIES} intentos")

    # actualizar metadata en DB
    update_last_scraped_date(today)
    print(f"\n Última fecha de scraping actualizada a: {today}")

if __name__ == "__main__":
    run_scraper()
