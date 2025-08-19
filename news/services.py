from datetime import datetime
from transformers import pipeline
from .scraping import NewsScraper

sentiment_analyzer = pipeline("sentiment-analysis")


def get_news_with_sentiment(query: str, start_date: datetime, end_date: datetime, 
                            financial_business_news_domains=None, max_articles: int = 25):
    
    if financial_business_news_domains is None:
        financial_business_news_domains = [
            "economictimes.indiatimes.com", "business-standard.com", "financialexpress.com", 
            "livemint.com", "thehindubusinessline.com", "moneycontrol.com", "bloombergquint.com", 
            "cnbctv18.com", "businesstoday.in", "forbesindia.com", "reuters.com", "bloomberg.com", 
            "ft.com", "wsj.com", "cnbc.com", "marketwatch.com", "investing.com", "finance.yahoo.com", 
            "seekingalpha.com", "businessinsider.com"
        ]
   
   
    scraper = NewsScraper(financial_business_news_domains, max_articles=max_articles)
    results = scraper.scrape(query, start_date, end_date)

    # Agregar análisis de sentimiento a cada noticia
    for article in results:
        if "description" in article and article["description"]:
            sentiment = sentiment_analyzer(article["description"][:512])[0]  # limitar longitud
            article["sentiment"] = {
                "label": sentiment["label"],
                "score": round(sentiment["score"], 2)
            }
        else:
            article["sentiment"] = {"label": "NEUTRAL", "score": 0.0}

    return results