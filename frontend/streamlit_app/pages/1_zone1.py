import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import requests
import time
import os
import base64
import textwrap
import random
import numpy as np
from datetime import datetime, timedelta

# charts
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# utils
from utils.config import API_KEY, MONGO_URI, DB_NAME, CITY
from utils.conversion import fahrenheitToCelsius
from utils.icons import get_icon
from utils.styles import load_css
from utils.weather import fetch_weather_data
from utils.db import load_latest_reading, load_history, load_readings
from utils.layout import (
    render_zone_header,
    render_refresh_update,
    render_api_update,
    render_metrics_row,
    render_section_header,
    HANGING_ICON,
    dashboard_title_metric_section,
)

# ---- page config ----
st.set_page_config(page_title="Zones", layout="wide")
load_css()


render_zone_header("zone 1")#renders title
render_refresh_update() #render btn refresh
render_api_update() #render api for testing





# ----------------------------
# Choose data source:
# Mongo first if it has values, otherwise API fallback
# ----------------------------
mongo_latest = load_latest_reading(zone="zone1", area="upper_plants", source="openweather")
temperature_cel, humidity, description, debug = fetch_weather_data()

# Start with API values
temp = temperature_cel
weather = description

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


# These do NOT exist in OpenWeather docs yet (keep None until sensors are ingested)
light = None
soil = None



hist_df = load_history(zone="zone1", area="upper_plants", source="openweather")




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




st.subheader("Adjust the data")

show_latest_only = st.toggle("Default: shows latest data only", value=True)

if show_latest_only:
    limit = 1
else:
    limit = st.slider("Rows", min_value=1, max_value=90, value=20, step=1)

docs = load_readings(zone="zone1", area="upper_plants", source="openweather", limit=limit)
table_df = pd.DataFrame(docs)

if table_df.empty:
    st.info("No readings found for upper plants yet.")
else:
    if "ts" in table_df.columns:
        table_df["ts"] = pd.to_datetime(table_df["ts"])
    st.dataframe(table_df, use_container_width=True)

st.markdown("---")





