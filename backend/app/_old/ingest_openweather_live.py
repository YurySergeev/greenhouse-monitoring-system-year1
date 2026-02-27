from app.mongo import get_collection  # or however you access mongo
import requests
import os

def fetch_and_store(zone="zone1", area="upper_plants", source="openweather"):
    """
    Pull current weather from OpenWeather and update ONE daily doc with rolling min/max.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    lat = os.getenv("OPENWEATHER_LAT")
    lon = os.getenv("OPENWEATHER_LON")

    if not api_key or not lat or not lon:
        raise RuntimeError("Missing OPENWEATHER_API_KEY / OPENWEATHER_LAT / OPENWEATHER_LON in .env")

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "imperial"}  # or metric

    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    temp_now = data["main"]["temp"]
    humidity = data["main"].get("humidity")
    pressure = data["main"].get("pressure")

    # choose your collection name
    col = get_collection("daily_weather")  # example
    upsert_daily(col, zone, area, source, temp_now, humidity, pressure)col, zone, area, source, temp_now, humidity, pressure)