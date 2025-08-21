from pymongo import MongoClient
from django.conf import settings

def get_mongo_client():
    if "URI" in settings.MONGO_DB:  
        client = MongoClient(settings.MONGO_DB["URI"])
    else:  
        client = MongoClient(settings.MONGO_DB["HOST"], settings.MONGO_DB["PORT"])
    return client[settings.MONGO_DB["NAME"]]