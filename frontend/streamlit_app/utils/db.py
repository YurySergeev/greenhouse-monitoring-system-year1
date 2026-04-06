from pymongo import MongoClient
import certifi
import streamlit as st
import pandas as pd
from utils.config import MONGO_URI, DB_NAME


# --------------------------------------------------
# Shared connection
# --------------------------------------------------

@st.cache_resource
def init_connection():
    if not MONGO_URI or not DB_NAME:
        return None, None
    client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    return client, db


# --------------------------------------------------
# OpenWeather data  (collection: weather_data)
# --------------------------------------------------

@st.cache_data(ttl=15)
def load_latest_reading(zone="zone1", area="upper_plants", source="openweather"):
    client, db = init_connection()
    if db is None:
        return None
    doc = db.weather_data.find_one(
        {"zone": zone, "area": area, "source": source},
        sort=[("ts", -1)]
    )
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


@st.cache_data(ttl=60)
def load_history(zone="zone1", area="upper_plants", source="openweather", hours=24):
    client, db = init_connection()
    if db is None:
        return pd.DataFrame()
    since = pd.Timestamp.utcnow() - pd.Timedelta(hours=hours)
    docs = list(db.weather_data.find(
        {"zone": zone, "area": area, "source": source,
         "ts": {"$gte": since.to_pydatetime()}},
        {"_id": 0, "ts": 1, "temp_c": 1, "humidity_pct": 1, "weather_desc": 1}
    ).sort("ts", 1))
    df = pd.DataFrame(docs)
    if not df.empty and "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"])
    return df


@st.cache_data(ttl=30)
def load_readings(zone="zone1", area="upper_plants", source="openweather", limit=50):
    client, db = init_connection()
    if db is None:
        return []
    docs = list(
        db.weather_data.find(
            {"zone": zone, "area": area, "source": source},
            {"raw": 0}
        ).sort("ts", -1).limit(limit)
    )
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs


# --------------------------------------------------
# Pico W sensor data  (collection: sensor_readings)
# --------------------------------------------------

@st.cache_data(ttl=15)
def load_latest_sensor(zone="zone1", area="upper_plants"):
    """
    Returns the most recent document from the Pico W sensor_readings collection.
    Fields: node_id, zone, area, source, temperature_c, humidity_rh, ts
    """
    client, db = init_connection()
    if db is None:
        return None
    doc = db.sensor_readings.find_one(
        {"zone": zone, "area": area, "source": "pico_w"},
        sort=[("ts", -1)]
    )
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


@st.cache_data(ttl=60)
def load_sensor_history(zone="zone1", area="upper_plants", hours=24):
    """
    Returns a DataFrame of Pico W readings for the past `hours` hours.
    Columns: ts, temperature_c, humidity_rh
    """
    client, db = init_connection()
    if db is None:
        return pd.DataFrame()
    since = pd.Timestamp.utcnow() - pd.Timedelta(hours=hours)
    docs = list(db.sensor_readings.find(
        {"zone": zone, "area": area, "source": "pico_w",
         "ts": {"$gte": since.to_pydatetime()}},
        {"_id": 0, "ts": 1, "temperature_c": 1, "humidity_rh": 1, "node_id": 1}
    ).sort("ts", 1))
    df = pd.DataFrame(docs)
    if not df.empty and "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"])
    return df


@st.cache_data(ttl=30)
def load_sensor_readings(zone="zone1", area="upper_plants", limit=50):
    """
    Returns raw Pico W documents for the data table.
    """
    client, db = init_connection()
    if db is None:
        return []
    docs = list(
        db.sensor_readings.find(
            {"zone": zone, "area": area, "source": "pico_w"},
        ).sort("ts", -1).limit(limit)
    )
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs