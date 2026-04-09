import requests
import pandas as pd

FLASK_BASE_URL = "http://localhost:5000"

# non-sensor fetching

def fetch_latest():
    try:
        res = requests.get(
            f"{FLASK_BASE_URL}/latest",
            params={
                "zone": "zone1",
                "area": "upper_plants",
                "source": "openweather"
            }
        )
        return res.json() if res.status_code == 200 else None
    except Exception:
        return None

def fetch_history():
    try:
        res = requests.get(
            f"{FLASK_BASE_URL}/history",
            params={
                "zone": "zone1",
                "area": "upper_plants",
                "source": "openweather"
            }
        )
        if res.status_code == 200:
            df = pd.DataFrame(res.json())
            if not df.empty and "ts" in df.columns:
                df["ts"] = pd.to_datetime(df["ts"])
            return df
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def fetch_readings(limit=20):
    try:
        res = requests.get(
            f"{FLASK_BASE_URL}/readings",
            params={
                "zone": "zone1",
                "area": "upper_plants",
                "source": "openweather",
                "limit": limit
            }
        )

        if res.status_code == 200:
            df = pd.DataFrame(res.json())

            if not df.empty and "ts" in df.columns:
                df["ts"] = pd.to_datetime(df["ts"])

            return df

        return pd.DataFrame()

    except Exception:
        return pd.DataFrame()

# -----------------------------
# SENSOR FETCHING
# -----------------------------

def fetch_latest_sensor():
    try:
        res = requests.get(
            f"{FLASK_BASE_URL}/api/sensor/latest",
            params={
                "zone": "zone1",
                "area": "upper_plants"
            }
        )
        return res.json() if res.status_code == 200 else None
    except Exception:
        return None


def fetch_sensor_history(hours=24, start_ts=None, end_ts=None):
    try:
        params = {
            "zone": "zone1",
            "area": "upper_plants",
        }

        if start_ts and end_ts:
            params["start_ts"] = start_ts
            params["end_ts"] = end_ts
        else:
            params["hours"] = hours

        res = requests.get(
            f"{FLASK_BASE_URL}/api/sensor/history",
            params=params
        )

        if res.status_code == 200:
            df = pd.DataFrame(res.json())
            if not df.empty and "ts" in df.columns:
                df["ts"] = pd.to_datetime(df["ts"])
            return df

        return pd.DataFrame()

    except Exception:
        return pd.DataFrame()

def fetch_sensor_readings(limit=50):
    try:
        res = requests.get(
            f"{FLASK_BASE_URL}/api/sensor/readings",
            params={
                "zone": "zone1",
                "area": "upper_plants",
                "limit": limit
            }
        )

        if res.status_code == 200:
            df = pd.DataFrame(res.json())

            if not df.empty and "ts" in df.columns:
                df["ts"] = pd.to_datetime(df["ts"])

            return df

        return pd.DataFrame()

    except Exception:
        return pd.DataFrame()