from pymongo import MongoClient
import certifi
import streamlit as st
import pandas as pd
from utils.config import MONGO_URI, DB_NAME

#Create single cached connection
@st.cache_resource
def init_connection():
    if not MONGO_URI or not DB_NAME:
        return None, None
    client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    return client, db



@st.cache_data(ttl=15)
def load_latest_reading(zone="zone1", area="upper_plants", source="openweather"):
    
    client, db = init_connection()
    if db is None: return None  # <-- FIXED: Explicitly checking against None
    
    doc = db.weather_data.find_one(
        {"zone": zone, "area": area, "source": source},
        sort=[("ts", -1)]
    )
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc
    
    """ 
    if not MONGO_URI or not DB_NAME:
        return None
    client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    doc = db.weather_data.find_one(  # ← was db.readings
        {"zone": zone, "area": area, "source": source},
        sort=[("ts", -1)]
    )
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc
    """

@st.cache_data(ttl=60)
def load_history(zone="zone1", area="upper_plants", source="openweather", hours=24):
    
    client, db = init_connection()
    if db is None: return pd.DataFrame() # <-- FIXED
    
    since = pd.Timestamp.utcnow() - pd.Timedelta(hours=hours)
    docs = list(db.weather_data.find(
        {
            "zone": zone,
            "area": area,
            "source": source,
            "ts": {"$gte": since.to_pydatetime()}
        },
        {"_id": 0, "ts": 1, "temp_c": 1, "humidity_pct": 1, "weather_desc": 1}
    ).sort("ts", 1))

    df = pd.DataFrame(docs)
    if not df.empty and "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"])
    return df


    """
    if not MONGO_URI or not DB_NAME:
        return pd.DataFrame()
    client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    since = pd.Timestamp.utcnow() - pd.Timedelta(hours=hours)
    docs = list(db.weather_data.find(  # ← was db.readings
        {
            "zone": zone,
            "area": area,
            "source": source,
            "ts": {"$gte": since.to_pydatetime()}
        },
        {"_id": 0, "ts": 1, "temp_c": 1, "humidity_pct": 1, "weather_desc": 1}
    ).sort("ts", 1))

    df = pd.DataFrame(docs)
    if not df.empty and "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"])
    return df
    """
    


# ---- Table: show readings for this zone/area/source ----
@st.cache_data(ttl=30)
def load_readings(zone="zone1", area="upper_plants", source="openweather", limit=50):
    
    client, db = init_connection()
    if db is None: return [] # <--
    
    docs = list(
        db.weather_data.find(
            {"zone": zone, "area": area, "source": source},
            {"raw": 0}
        ).sort("ts", -1).limit(limit)
    )
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs

    """
    if not MONGO_URI or not DB_NAME:
        return []
    client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    docs = list(
        db.weather_data.find(
            {"zone": zone, "area": area, "source": source},
            {"raw": 0}
        ).sort("ts", -1).limit(limit)
    )
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs
    """