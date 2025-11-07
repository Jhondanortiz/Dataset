# api/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)
database = client[settings.DATABASE_NAME]
collection = database[settings.COLLECTION_NAME]

# Para pruebas sincrónicas (opcional)
from pymongo import MongoClient
sync_client = MongoClient(settings.MONGODB_URL)
sync_db = sync_client[settings.DATABASE_NAME]
sync_collection = sync_db[settings.COLLECTION_NAME]