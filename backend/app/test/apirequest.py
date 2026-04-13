from datetime import datetime, timezone
import requests
import pymongo
import schedule
import time
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "greenhouse_db")

collection = None

def init_db_collection():
    global collection
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db = client[DB_NAME]
        collection = db["weather_data"]
        collection.create_index("ts")
        print("Successfully connected to MongoDB.")
    except Exception as e:
        collection = None
        print(f"Database connection failed: {e}")


def get_weather():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Missing OPENWEATHER_API_KEY in .env")
        return None

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "lat": 41.0814,
        "lon": -81.5190,
        "appid": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        print("weather:", data["weather"][0]["description"])
        print("Temperature:", data["main"]["temp"])
        print("temp_min:", data["main"]["temp_min"])
        print("temp_max:", data["main"]["temp_max"])
        print("Humidity:", data["main"]["humidity"])
        print("City", data["name"])
        print("Timestamp:", datetime.now(timezone.utc))
        return data
    except requests.RequestException as e:
        print(f"Weather API request failed: {e}")
        return None


def transform_data(api_data):
    record = {
        "zone": "zone1",
        "area": "upper_plants",
        "source": "openweather",
        "sensor_type": "weather",
        "temp_c": api_data["main"]["temp"],
        "humidity_pct": api_data["main"]["humidity"],
        "city": api_data["name"],
        "temp_min": api_data["main"]["temp_min"],
        "temp_max": api_data["main"]["temp_max"],
        "weather_desc": api_data["weather"][0]["description"],
        "ts": datetime.now(timezone.utc)
    }
    return record


def save_data(records):
    if records and collection is not None:
        collection.insert_one(records)
        print(f"Data saved at {datetime.now(timezone.utc)}")


def collect_data_to_db():
    api_data = get_weather()
    if api_data:
        final_data = transform_data(api_data)
        save_data(final_data)


def run_scheduler(interval_minutes=20):
    init_db_collection()
    collect_data_to_db()
    schedule.every(interval_minutes).minutes.do(collect_data_to_db)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    run_scheduler()