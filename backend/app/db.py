import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)
db = _client[os.getenv("DB_NAME")]

#we need a toggler here