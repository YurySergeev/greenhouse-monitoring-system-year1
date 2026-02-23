import os
from datetime import datetime, timezone
import requests
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv


# Load environment variables
load_dotenv(find_dotenv())

API_KEY = (os.getenv("OPENWEATHER_API_KEY") or "").strip()
MONGO_URI = (os.getenv("MONGO_URI") or "").strip()
DB_NAME = (os.getenv("DB_NAME") or "").strip()

CITY = "Akron,US"


def fetch_openweather(city: str):
    """
    Fetch current weather from OpenWeather in Celsius (metric mode).
    Returns dictionary ready for Mongo.
    """
    if not API_KEY:
        raise RuntimeError("OPENWEATHER_API_KEY missing")

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&units=metric&appid={API_KEY}"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    main = data.get("main", {})
    weather_arr = data.get("weather", [{}])

    temp_c = main.get("temp")
    humidity = main.get("humidity")
    desc = (weather_arr[0] or {}).get("description")

    if temp_c is None or humidity is None:
        raise RuntimeError("Weather API returned incomplete data")

    return {
        "temp_c": temp_c,
        "humidity_pct": humidity,
        "weather_desc": desc,
    }


def main():
    """
    Fetch weather and insert into MongoDB.
    This will run every 5 minutes via cron or scheduler.
    """
    if not MONGO_URI or not DB_NAME:
        raise RuntimeError("Mongo credentials missing")

    print("Fetching weather...")

    weather = fetch_openweather(CITY)

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    document = {
        "zone": "zone1",
        "area": "upper_plants",
        "source": "openweather",
        "ts": datetime.now(timezone.utc),
        **weather,
    }

    db.readings.insert_one(document)

    print("Inserted at:", document["ts"])
    print("Temp (C):", weather["temp_c"])
    print("Humidity:", weather["humidity_pct"], "%")


if __name__ == "__main__":
    main()