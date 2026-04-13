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
def load_history(zone="zone1", area="upper_plants", source="openweather", hours=24, start_ts=None, end_ts=None):
    client, db = init_connection()
    if db is None:
        return pd.DataFrame()
        
    # Build the time query (Custom Range vs Last X Hours)
    if start_ts and end_ts:
        ts_query = {"$gte": start_ts, "$lte": end_ts}
    else:
        since = pd.Timestamp.utcnow() - pd.Timedelta(hours=hours)
        ts_query = {"$gte": since.to_pydatetime()}

    docs = list(db.weather_data.find(
        {"zone": zone, "area": area, "source": source, "ts": ts_query},
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
    doc = db.zone1_dht22_test.find_one(
        {"zone": zone, "area": area, "source": "pico_w"},
        sort=[("ts", -1)]
    )
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


@st.cache_data(ttl=60)
def load_sensor_history(zone="zone1", area="upper_plants", hours=24, start_ts=None, end_ts=None):
    """
    Returns a DataFrame of Pico W readings based on hours or a specific date range.
    """
    client, db = init_connection()
    if db is None:
        return pd.DataFrame()
        
    # Build the time query
    if start_ts and end_ts:
        ts_query = {"$gte": start_ts, "$lte": end_ts}
    else:
        since = pd.Timestamp.utcnow() - pd.Timedelta(hours=hours)
        ts_query = {"$gte": since.to_pydatetime()}

    docs = list(db.zone1_dht22_test.find(
        {"zone": zone, "area": area, "source": "pico_w", "ts": ts_query},
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
        db.zone1_dht22_test.find(
            {"zone": zone, "area": area, "source": "pico_w"},
        ).sort("ts", -1).limit(limit)
    )
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs