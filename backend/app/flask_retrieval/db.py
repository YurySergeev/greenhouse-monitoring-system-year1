from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "greenhouse_db")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["weather_data"]

def insert_data(record):
    collection.insert_one(record)

def get_all_data():
    return list(collection.find({}, {"_id": 0}))

def get_zone_data(zone_name):
    return list(collection.find({"zone": zone_name}, {"_id": 0}))

def get_latest(zone=None, area=None, source=None):
    query = {}
    if zone:
        query["zone"] = zone
    if area:
        query["area"] = area
    if source:
        query["source"] = source
    result = collection.find_one(query, {"_id": 0}, sort=[("ts", -1)])
    return result or {}

def get_history(zone=None, area=None, source=None):
    query = {}
    if zone:
        query["zone"] = zone
    if area:
        query["area"] = area
    if source:
        query["source"] = source
    return list(collection.find(query, {"_id": 0}).sort("ts", 1))

def get_readings(zone=None, area=None, source=None, limit=20):
    query = {}
    if zone:
        query["zone"] = zone
    if area:
        query["area"] = area
    if source:
        query["source"] = source
    return list(collection.find(query, {"_id": 0}).sort("ts", -1).limit(limit))

