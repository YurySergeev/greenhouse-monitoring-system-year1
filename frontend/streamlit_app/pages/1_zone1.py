import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from multiprocessing.util import close_all_fds_except
from urllib import response
import streamlit as st

from datetime import datetime, timedelta

import os
from streamlit import subheader
import requests
import time

from tenacity import stop_never

from utils.conversion import fahrenheitToCelsius
from dotenv import load_dotenv
from pathlib import Path
from utils.icons import get_icon
import base64
import textwrap
#------------------ libraries for plats sections  and charts -----------------
import pandas as pd
import numpy as np
from datetime import datetime
import textwrap
import random # this will generate random numbers to use it as mmock for hecking status conditions on zone plnat

#--------------------------- charts libraries
import plotly.express as px
import plotly.graph_objects as go #gauge chart

#----------------------------- database down here
from pymongo import MongoClient
from dotenv import load_dotenv
#-------------------------------

from dotenv import load_dotenv, find_dotenv

# ----- frontend/assets/css
from pathlib import Path
from utils.styles import load_css
#---- render from utils.layout

from utils.layout import (
    render_zone_header,
    render_refresh_update,
    render_api_update,
    render_metrics_row,
    render_section_header,
    HANGING_ICON,
    dashboard_title_metric_section,


)
from utils.styles import load_css

#  utilities
# from utils.conversion import fahrenheitToCelsius
# from utils.icons import get_icon  # assuming you have this
# NOTE: keep  imports as they are in your project

# ----------------------------
# Config / Env
# ----------------------------
st.set_page_config(page_title="Zones", layout="wide")

# Load .env ONCE, robustly (finds it up the folder tree)
load_dotenv(find_dotenv())

API_KEY = (os.getenv("OPENWEATHER_API_KEY") or "").strip()
MONGO_URI = (os.getenv("MONGO_URI") or "").strip()
DB_NAME = (os.getenv("DB_NAME") or "").strip()





#renders title
render_zone_header("zone 1")
render_refresh_update()
render_api_update()

CITY = "Akron,US"  # more reliable than just Akron


#will prevent the hit the api everytime the page reruns
@st.cache_data(ttl=300)  # cache expires after 300 seconds = 5 minutes
def fetch_weather_data(api_key: str, city: str):
    if not api_key:
        return None, None, None, {"error": "Missing OPENWEATHER_API_KEY"} #safety check

    #build the api url
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid={api_key}"

    try:
        resp = requests.get(url, timeout=10) #send the GET api request
        debug = { #debug object
            "url": url,
            "status_code": resp.status_code,
            "text_preview": resp.text[:300],
        }

        #handle non-200 response, if the city is invalid, api is wrong
        if resp.status_code != 200:
            return None, None, None, debug
        #parse json converting response text into a ptython dic
        data = resp.json()

        #extract fields
        main = data.get("main") or {}
        weather_arr = data.get("weather") or [{}]

        #extract values
        temp_f = main.get("temp")
        humidity = main.get("humidity")
        desc = (weather_arr[0] or {}).get("description")

        #if api response changed its json format  -> throws errors
        if temp_f is None or humidity is None or desc is None:
            debug["parse_error"] = "Missing expected fields in JSON"
            debug["json_keys"] = list(data.keys())
            return None, None, None, debug

        #convert fah to cel
        temp_c = fahrenheitToCelsius(temp_f)

        #succefully return this
        return temp_c, humidity, desc, debug

    #exception handling if json is broken, request timeout or no internet
    except Exception as e:
        return None, None, None, {"error": str(e)}

# ----------------------------
# Mongo: latest reading (cached)
# ----------------------------

import certifi
from pymongo import MongoClient

#cache this function for 15 seconds
@st.cache_data(ttl=15)
def load_latest_reading(zone="zone1", area="upper_plants", source="openweather"):
    #if variables are missing to try to make connection
    if not MONGO_URI or not DB_NAME: #safety check
        return None
    #create monogo client
    #Mongo db atltas
    #secure cloud db connection
    client = MongoClient(
        MONGO_URI, #connect the string
        tls=True, #ecnvyprted the connection
        tlsCAFile=certifi.where() #validation
    )

    #select db = greenhouse_+db
    db = client[DB_NAME]

    #querying collectiob for db
    doc = db.readings.find_one(
        { #filter
            "zone": zone,
            "area": area,
            "source": source
        },
        sort=[("ts", -1)] #sort by timestamp , descending order, newest first
    )

    #mongo db _id is an object
    #the id will be convert into a string
    #if not gives the string convertion, json will give error
    if doc:
        doc["_id"] = str(doc["_id"])

    return doc #retutn the document, or nothing if is not found

# ----------------------------
# Choose data source:
# Mongo first if it has values, otherwise API fallback
# ----------------------------
mongo_latest = load_latest_reading(
    zone="zone1",
    area="upper_plants",
    source="openweather"
)
api_temp, api_humidity, api_weather, api_debug = fetch_weather_data(API_KEY, CITY)

# Start with API values
temp = api_temp
humidity = api_humidity
weather = api_weather

# Override ONLY when mongo doc exists AND has values
if mongo_latest:
    mongo_temp = mongo_latest.get("temp_c")
    mongo_humidity = mongo_latest.get("humidity_pct")
    mongo_weather = mongo_latest.get("weather_desc") or mongo_latest.get("weather")

    if mongo_temp is not None:
        temp = mongo_temp
    if mongo_humidity is not None:
        humidity = mongo_humidity
    if mongo_weather is not None:
        weather = mongo_weather

# Debug info (remove later)
with st.expander("Debug: Weather sources", expanded=False):
    st.write("Mongo latest:", mongo_latest)
    st.write("API debug:", api_debug)
    st.write("Final values:", {"temp": temp, "humidity": humidity, "weather": weather})



render_metrics_row(temp, humidity,weather)
render_section_header("Hanging Plants Zone1", HANGING_ICON)
dashboard_title_metric_section()


#section selection, control box and alert box
def sidebar_control_func():
    load_css()  #loads the css
    st.sidebar.header("Zone 1")

    if "zone1_section" not in st.session_state:
        st.session_state["zone1_section"] = "Upper Plants"

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Upper Plants", use_container_width=True):
            st.session_state["zone1_section"] = "Upper Plants"

    with col2:
        if st.button("Middle Plants", use_container_width=True):
            st.session_state["zone1_section"] = "Middle Plants"

    with col3:
        if st.button("Ground Plants", use_container_width=True):
            st.session_state["zone1_section"] = "Ground Plants"

    st.sidebar.divider()

    section = st.session_state["zone1_section"]
    st.sidebar.write(f"Selected: **{section}**")



    if section == "Upper Plants":
        st.divider()

        col_controls, col_alerts = st.columns(2) #columns

        with col_controls:
            with st.container(border=True):
                st.markdown("#### ⚙️ Controls")
                unit = st.radio("Temperature Unit", ["°C", "°F"], horizontal=True, label_visibility="collapsed",
                                key="temp_unit")

        with col_alerts:
            with st.container(border=True):
                st.markdown("#### 🚨 Upper Section Alerts")
                st.write("Coming soon…")
                st.markdown("<br>", unsafe_allow_html=True)


        return section, unit

    return section, None


        # upper_plntas_func() #here will live dashboards for upper plants



def main():
    section, unit = sidebar_control_func()





if __name__ == "__main__":
    main()















ZONE = "zone1"
AREA = "upper_plants"
SOURCE = "openweather"

# ---- Load latest reading (OpenWeather) ----
@st.cache_data(ttl=15)
def load_latest(zone, area, source):
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME")]
    doc = db.readings.find_one(
        {"zone": zone, "area": area, "source": source},
        sort=[("ts", -1)]
    )
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

latest = load_latest(ZONE, AREA, SOURCE)

# Pull values from latest (OpenWeather fields)
temp = latest.get("temp_c") if latest else None
humidity = latest.get("humidity_pct") if latest else None
weather = latest.get("weather_desc") if latest else None

# These do NOT exist in OpenWeather docs yet (keep None until sensors are ingested)
light = None
soil = None

# ---- Load history for charts (OpenWeather) ----
@st.cache_data(ttl=60)
def load_history(zone, area, source, hours=24):
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME")]
    since = pd.Timestamp.utcnow() - pd.Timedelta(hours=hours)

    docs = list(
        db.readings.find(
            {
                "zone": zone,
                "area": area,
                "source": source,
                "ts": {"$gte": since.to_pydatetime()}
            },
            {"_id": 0, "ts": 1, "temp_c": 1, "humidity_pct": 1, "weather_desc": 1}
        ).sort("ts", 1)
    )

    df = pd.DataFrame(docs)
    if not df.empty and "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"])
    return df

hist_df = load_history(ZONE, AREA, SOURCE)






# ---- Metrics row ----
k1, k2, k3, k4 = st.columns(4)

with k1:
    if temp is None:
        st.metric("Temperature", "N/A")
    else:
        st.metric("Temperature", f"{float(temp):.1f} °C")

with k2:
    if humidity is None:
        st.metric("Humidity", "N/A")
    else:
        st.metric("Humidity", f"{float(humidity):.0f} %")

with k3:
    # placeholder until sensors exist
    st.metric("Light", "N/A")

with k4:
    # placeholder until sensors exist
    st.metric("Soil", "N/A")


# ---- Charts ----
c1, c2 = st.columns(2)

with c1:
    if not hist_df.empty and "temp_c" in hist_df.columns and hist_df["temp_c"].notna().any():

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hist_df["ts"],
            y=hist_df["temp_c"],
            mode="lines+markers",        # straight line + dots
            line=dict(shape="linear"),   # explicitly linear
            name="Temperature"
        ))

        fig.update_layout(
            template="plotly_dark",
            title="Temperature (°C)",
            xaxis_title="Time",
            yaxis_title="°C",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No temperature history yet (from openweather).")

with c2:
    if not hist_df.empty and "humidity_pct" in hist_df.columns and hist_df["humidity_pct"].notna().any():
        fig = px.line(
            hist_df, x="ts",
            y="humidity_pct",
            template="plotly_dark",
            title="Humidity (%)",
             markers=True
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No humidity history yet (from openweather).")


# ---- Gauge + Light placeholder ----
c3, c4 = st.columns(2)

with c3:
    # soil gauge is ONLY when sensors exist
    st.info("Soil gauge will show once sensors are ingested (source='sensors').")

with c4:
    st.markdown("""
    <div style="
        background-color:none;
        padding:30px;
        border-radius:12px;
        text-align:center;
        border:1px ;
    ">
        <h3 style="margin-bottom:10px;">Light (lx)</h3>
        <p style="color:#9CA3AF; font-size:14px;">
            Dashboard coming soon.
        </p>
    </div>
    """, unsafe_allow_html=True)








# ---- Table: show readings for this zone/area/source ----
@st.cache_data(ttl=30)
def load_readings(zone, area, source, limit=50):
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME")]
    docs = list(
        db.readings.find(
            {"zone": zone, "area": area, "source": source},
            {"raw": 0}
        ).sort("ts", -1).limit(limit)
    )
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs

st.subheader("Adjust the data")

show_latest_only = st.toggle("Default: shows latest data only", value=True)

if show_latest_only:
    limit = 1
else:
    limit = st.slider("Rows", min_value=1, max_value=90, value=20, step=1)

docs = load_readings(ZONE, AREA, SOURCE, limit=limit)
table_df = pd.DataFrame(docs)

if table_df.empty:
    st.info("No readings found for upper plants yet.")
else:
    if "ts" in table_df.columns:
        table_df["ts"] = pd.to_datetime(table_df["ts"])
    st.dataframe(table_df, use_container_width=True)

st.markdown("---")





