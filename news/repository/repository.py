from datetime import datetime
from pymongo import ASCENDING
from mongo_client import get_mongo_client

class NewsRepository:
    def __init__(self):
        self.db = get_mongo_client()
        self.collection = self.db.news
        self.metadata_collection = self.db.scraping_metadata
        self.ensure_indexes()

    def ensure_indexes(self):
        self.collection.create_index([("date", ASCENDING)])
        self.collection.create_index([("source", ASCENDING)])
        self.collection.create_index([("category", ASCENDING)])
        self.metadata_collection.create_index("key", unique=True)

    def get_news(self, category: str = None, source=None, start_date=None, end_date=None, limit=20):
        query = {}
        if category:
            query["category"] = category
        
        if source:
            if isinstance(source, list):
                query["source"] = {"$in": source}  # múltiples fuentes
            else:
                query["source"] = source  # caso de un solo string
        
        if start_date and end_date:
            query["date"] = {"$gte": start_date, "$lte": end_date}
        
        return list(self.collection.find(query).sort("date", -1).limit(limit))

    def get_unique_sources(self):
        return self.collection.distinct("source")

    def insert_news(self, news_item: dict):
        if isinstance(news_item.get("date"), str):
            news_item["date"] = datetime.strptime(news_item["date"], "%Y-%m-%d")
        
        return self.collection.insert_one(news_item).inserted_id

    def insert_many_news(self, news_list: list):
        for news_item in news_list:
            if isinstance(news_item.get("date"), str):
                news_item["date"] = datetime.strptime(news_item["date"], "%Y-%m-%d")
                
        print(f"Insertando en Mongo: {len(news_list)} artículos")
        return self.collection.insert_many(news_list).inserted_ids

    def get_metadata(self, key: str):
        record = self.metadata_collection.find_one({"key": key})
        return record["value"] if record else None

    def update_metadata(self, key: str, value):
        self.metadata_collection.update_one(
            {"key": key},
            {"$set": {"value": value, "updated_at": datetime.utcnow()}},
            upsert=True
        )

