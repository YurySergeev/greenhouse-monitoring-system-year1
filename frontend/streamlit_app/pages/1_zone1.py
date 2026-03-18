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
    render_zone1_top_controls,

)

# ---- page config ----
st.set_page_config(page_title="Zones", layout="wide")
load_css()

render_zone_header("zone 1")#renders title
render_refresh_update() #render btn refresh
render_api_update() #render api for testing
section, unit = render_zone1_top_controls()

# ----------------------------
# Choose data source:
# Mongo first if it has values, otherwise API fallback
# ----------------------------
mongo_latest = load_latest_reading(zone="zone1", area="upper_plants", source="openweather")
temperature_cel, humidity, description, debug = fetch_weather_data()

# Start with API values
temp = temperature_cel
weather = description
render_metrics_row(temp, humidity, weather) #metric box boxes

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



hist_df = load_history(zone="zone1", area="upper_plants", source="openweather")
render_section_header("Upper Plants", HANGING_ICON) #render title section

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
            mode="lines+markers",
            name="Temperature",
            line=dict(width=3),
            marker=dict(size=8)
        ))

        y_min = hist_df["temp_c"].min() - 0.01
        y_max = hist_df["temp_c"].max() + 0.01

        fig.update_layout(
            template="plotly_dark",
            title="Temperature Trend",
            xaxis_title="Time",
            yaxis_title="°C",
            hovermode="x unified",
            yaxis=dict(range=[y_min, y_max]),
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

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
    soil_value = 5.5  # replace later with real sensor value

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=soil_value,
        title={"text": "Soil Moisture (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"thickness": 0.3},
            "steps": [
                {"range": [0, 25], "color": "#5c1f1f"},
                {"range": [25, 45], "color": "#2e6b3e"},
                {"range": [45, 70], "color": "#7a5a1d"},
                {"range": [70, 100], "color": "#1f3c5c"},
            ],
            "threshold": {
                "line": {"width": 4},
                "thickness": 0.8,
                "value": soil_value
            }
        }
    ))

    fig.update_layout(
        template="plotly_dark",
        height=320,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
with c4:
    if (
        not hist_df.empty
        and "temp_c" in hist_df.columns
        and "humidity_pct" in hist_df.columns
    ):

        fig = go.Figure()

        # Temperature line
        fig.add_trace(go.Scatter(
            x=hist_df["ts"],
            y=hist_df["temp_c"],
            mode="lines+markers",
            name="Temperature (°C)",
            line=dict(width=3, color="#4f6cff"),
            marker=dict(size=6),
            yaxis="y1"
        ))

        # Humidity line
        fig.add_trace(go.Scatter(
            x=hist_df["ts"],
            y=hist_df["humidity_pct"],
            mode="lines+markers",
            name="Humidity (%)",
            line=dict(width=3, color="#00c896", dash="dash"),
            marker=dict(size=6),
            yaxis="y2"
        ))

        fig.update_layout(
            template="plotly_dark",
            title="Temperature vs Humidity",
            xaxis=dict(title="Time"),

            # Left axis
            yaxis=dict(
                title="Temperature (°C)",
                side="left"
            ),

            # Right axis
            yaxis2=dict(
                title="Humidity (%)",
                overlaying="y",
                side="right"
            ),

            hovermode="x unified",
            legend=dict(
                orientation="h",
                y=1.1,
                x=0
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    else:
        st.info("No comparison data available yet.")
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





