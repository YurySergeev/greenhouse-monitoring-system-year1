import os
import requests
from datetime import datetime, timezone
from app.db.mongo import get_db


def day_key(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")


def upsert_daily(collection, zone, area, source, temp_now, humidity, pressure):
    now = datetime.now(timezone.utc)
    key = day_key(now)

    collection.update_one(
        {"zone": zone, "area": area, "source": source, "day": key},
        {
            "$setOnInsert": {
                "zone": zone,
                "area": area,
                "source": source,
                "day": key,
                "created_at": now,
                "temp_min_day": temp_now,
                "temp_max_day": temp_now,
            },
            "$set": {
                "last_temp": temp_now,
                "humidity": humidity,
                "pressure": pressure,
                "updated_at": now,
            },
            "$min": {"temp_min_day": temp_now},
            "$max": {"temp_max_day": temp_now},
        },
        upsert=True
    )


def fetch_and_store(zone="zone1", area="upper_plants", source="openweather"):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    lat = os.getenv("OPENWEATHER_LAT")
    lon = os.getenv("OPENWEATHER_LON")
    units = os.getenv("OPENWEATHER_UNITS", "imperial")

    if not api_key or not lat or not lon:
        raise RuntimeError("Missing OpenWeather env variables")

    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": units,
        },
        timeout=20,
    )
    response.raise_for_status()

    data = response.json()

    temp_now = data["main"]["temp"]
    humidity = data["main"].get("humidity")
    pressure = data["main"].get("pressure")

    db = get_db()
    collection = db["readings"]

    upsert_daily(collection, zone, area, source, temp_now, humidity, pressure)