import os
from pymongo import MongoClient

_client = None
_db = None

def init_mongo():
    global _client, _db

    uri = os.getenv("MONGO_URI")
    name = os.getenv("DB_NAME")

    if not uri or not name:
        raise RuntimeError("Missing MONGO_URI or DB_NAME in .env")

    _client = MongoClient(uri)
    _db = _client[name]

def get_db():
    global _db
    if _db is None:
        init_mongo()
    return _db