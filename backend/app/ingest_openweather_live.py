import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import requests

from pymongo import ASCENDING
from app.db import db

load_dotenv()

def ensure_indexes():
    db.readings.create_index(
        [("source", ASCENDING), ("zone", ASCENDING), ("day", ASCENDING)],
        unique=True,
    )

def fetch_weather_data_current():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city = os.getenv("OPENWEATHER_CITY", "Akron")
    country = os.getenv("OPENWEATHER_COUNTRY", "US")
    units = os.getenv("OPENWEATHER_UNITS", "metric")  # Celsius

    if not api_key:
        raise RuntimeError("Missing OPENWEATHER_API_KEY in .env")

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": f"{city},{country}",
        "appid": api_key,
        "units": units,
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def upsert_weather_data(zone="zone1_upper_plants"):


    data = fetch_weather_data_current()

    now_utc = datetime.now(timezone.utc)
    day = now_utc.date().isoformat()  # YYYY-MM-DD

    doc = {
        "source": "openweather",
        "zone": zone,
        "day": day,
        "ts": now_utc,

        "temp_c": float(data["main"]["temp"]),
        "humidity_pct": int(data["main"]["humidity"]),
        "weather_desc": data["weather"][0]["description"],
        "soil_moisture_pct": None,
    },



    result = db.readings.update_one(
        {"source": doc["source"], "zone": doc["zone"], "day": doc["day"]},
        {"$set": doc},
        upsert=True,
    )

    if result.upserted_id:
        print("✅ created new day doc:", result.upserted_id)
    else:
        print("✅ updated today's doc:", doc["day"])

    print("✅ ts:", doc["ts"].isoformat())

def main():
    upsert_weather_data(zone=os.getenv("ZONE", "zone1"))

if __name__ == "__main__":
    main()