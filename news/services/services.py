from datetime import datetime
from transformers import pipeline

from news import repository
from django.conf import settings

from datetime import datetime
from .scraping import NewsScraper

# Cargar el modelo de análisis de sentimiento (una sola vez)
sentiment_analyzer = pipeline("sentiment-analysis")


def scrape_news(query: str, start_date: datetime, end_date: datetime,
                financial_business_news_domains=None, max_articles: int = 25):
    
    if financial_business_news_domains is None:
        financial_business_news_domains = settings.FINANCIAL_NEWS_SOURCES

    scraper = NewsScraper(financial_business_news_domains, max_articles=max_articles)
    results = scraper.scrape(query, start_date, end_date)
    return results


def add_sentiment_analysis(articles: list):
   
    for article in articles:
        if "description" in article and article["description"]:
            sentiment = sentiment_analyzer(article["description"][:512])[0]  # limitar longitud
            article["sentiment"] = {
                "label": sentiment["label"],
                "score": round(sentiment["score"], 2)
            }
        else:
            article["sentiment"] = {"label": "NEUTRAL", "score": 0.0}
    return articles


def get_news_with_sentiment(query: str, start_date: datetime, end_date: datetime,
                            financial_business_news_domains=None, max_articles: int = 25):
   
    articles = scrape_news(query, start_date, end_date,
                           financial_business_news_domains, max_articles)
    return add_sentiment_analysis(articles)

def save_scraped_news(news_list):
  
    repository.ensure_indexes()
    return repository.insert_many_news(news_list)

def fetch_news(category, source=None, start_date=None, end_date=None, limit=20):

    return repository.get_news(category, source, start_date, end_date, limit)

def get_all_sources():

    return repository.get_unique_sources()
