from datetime import datetime
from transformers import pipeline




from news.repository.repository import NewsRepository
from django.conf import settings
from .scraping import NewsScraper

class NewsService:
        
    def __init__(self):
        self.repository = NewsRepository()
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
   

    def save_scraped_news(self, news_list):
        self.repository.ensure_indexes()
        return self.repository.insert_many_news(news_list)

    def fetch_news(self, category, source=None, start_date=None, end_date=None, limit=20):

        return self.repository.get_news( category, source, start_date, end_date, limit)

    def get_all_sources(self):
        return self.repository.get_unique_sources()
    

    def get_news_with_sentiment(self, query: str, start_date: datetime, end_date: datetime,
                                financial_business_news_domains=None, max_articles: int = 25):
    
        articles = self.scrape_news(query, start_date, end_date,
                            financial_business_news_domains, max_articles)
        return self.add_sentiment_analysis(articles)


    def scrape_news(self, query: str, start_date: datetime, end_date: datetime,
                    financial_business_news_domains=None, max_articles: int = 25):
        
        if financial_business_news_domains is None:
            financial_business_news_domains = settings.FINANCIAL_NEWS_SOURCES

        scraper = NewsScraper(financial_business_news_domains, max_articles=max_articles)
        results = scraper.scrape(query, start_date, end_date)
        return results


    def add_sentiment_analysis(self, articles: list):
    
        for article in articles:
            if "description" in article and article["description"]:
                sentiment = self.sentiment_analyzer(article["description"][:512])[0]  # limitar longitud
                article["sentiment"] = {
                    "label": sentiment["label"],
                    "score": round(sentiment["score"], 2)
                }
            else:
                article["sentiment"] = {"label": "NEUTRAL", "score": 0.0}
        return articles


    

    
