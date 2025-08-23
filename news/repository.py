from datetime import datetime
from pymongo import ASCENDING
from mongo_client import get_mongo_client

db = get_mongo_client()
collection = db.news
metadata_collection = db.scraping_metadata  


def ensure_indexes():
    collection.create_index([("date", ASCENDING)])
    collection.create_index([("source", ASCENDING)])
    collection.create_index([("category", ASCENDING)])
    metadata_collection.create_index("key", unique=True)  

def get_unique_sources():

    return collection.distinct("source")


def insert_news(news_item: dict):
    if isinstance(news_item.get("date"), str):
        news_item["date"] = datetime.strptime(news_item["date"], "%Y-%m-%d")
    
    return collection.insert_one(news_item).inserted_id


def insert_many_news(news_list: list):
    for news_item in news_list:
        if isinstance(news_item.get("date"), str):
            news_item["date"] = datetime.strptime(news_item["date"], "%Y-%m-%d")
            
    print(f"Insertando en Mongo: {len(news_item)} artículos")

    return collection.insert_many(news_list).inserted_ids


def get_metadata(key: str):
    record = metadata_collection.find_one({"key": key})
    return record["value"] if record else None


def update_metadata(key: str, value):
    metadata_collection.update_one(
        {"key": key},
        {"$set": {"value": value, "updated_at": datetime.utcnow()}},
        upsert=True
    )


def get_news(category: str = None, source: str = None, start_date=None, end_date=None, limit=20):
    
    query = {}
    if category:
        query["category"] = category
    if source:
        query["source"] = source
    if start_date and end_date:
        query["date"] = {"$gte": start_date, "$lte": end_date}
    
    return list(collection.find(query).sort("date", -1).limit(limit))
