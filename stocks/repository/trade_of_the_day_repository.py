from datetime import datetime, date
from pymongo import ASCENDING, DESCENDING
from mongo_client import get_mongo_client  

class TradeOfTheDayRepository:
    def __init__(self):
        self.db = get_mongo_client()
        self.collection = self.db.trade_of_the_day
        self.ensure_indexes()

    def ensure_indexes(self):
       
        self.collection.create_index([("date", ASCENDING)], unique=True)

    def save_trades(self, trades: list[dict]):
        for trade in trades:
            trade["date"] = datetime.combine(trade["date"], datetime.min.time())

        # Guardamos (upsert) todos los trades bajo la misma fecha
        self.collection.update_one(
            {"date": trades[0]["date"]},   # usamos la fecha como clave
            {"$set": {"date": trades[0]["date"], "trades": trades}},
            upsert=True
        )

        
    def get_trades_by_date(self, day: date):
        # Si ya viene como datetime.date, conviértelo a datetime (00:00:00)
        if isinstance(day, date) and not isinstance(day, datetime):
            day = datetime.combine(day, datetime.min.time())

        doc = self.collection.find_one({"date": day})
        return doc["trades"] if doc else []

    def get_trades_today(self):
       
        today = datetime.now().date()
        return self.get_trades_by_date(today)
    
    
    def get_most_recent_trade(self):
        """
        Obtiene el documento de trade más reciente (última fecha registrada)
        """
        doc = self.collection.find_one(sort=[("date", DESCENDING)])
        if not doc:
            return None

        # Convertir _id a string y la fecha a formato ISO
        doc["_id"] = str(doc["_id"])
        if isinstance(doc["date"], datetime):
            doc["date"] = doc["date"].isoformat()

        return doc["trades"] if doc else []
