import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from utils.config import CITY
from utils.styles import load_css
from utils.weather import fetch_weather_data
from utils.db import (
    load_latest_reading,
    load_history,
    load_readings,
    load_latest_sensor,
    load_sensor_history,
    load_sensor_readings,
)
from utils.layout import (
    render_zone_header,
    render_refresh_update,
    render_metrics_row,
    render_section_header,
    render_zone1_top_controls,
)
from utils.sidebar import render_sidebar

# ── Page config THEN CSS — must happen before any other st calls ───────────────
st.set_page_config(page_title="Zone 1", layout="wide")
load_css()  # ← must be here, right after set_page_config

render_sidebar()

# ── Header ─────────────────────────────────────────────────────────────────────
render_zone_header("Zone 1")
render_refresh_update()

section, unit = render_zone1_top_controls()

# ── Data sources ───────────────────────────────────────────────────────────────
# Priority: Pico W (inside greenhouse) > OpenWeather mongo > live API fallback

pico_latest  = load_latest_sensor(zone="zone1", area="upper_plants")
mongo_latest = load_latest_reading(zone="zone1", area="upper_plants", source="openweather")
api_temp, api_humidity, api_desc, _ = fetch_weather_data()

temp     = api_temp
humidity = api_humidity
weather  = api_desc

if mongo_latest:
    if mongo_latest.get("temp_c")       is not None: temp     = mongo_latest["temp_c"]
    if mongo_latest.get("humidity_pct") is not None: humidity = mongo_latest["humidity_pct"]
    if mongo_latest.get("weather_desc") is not None: weather  = mongo_latest["weather_desc"]

if pico_latest:
    if pico_latest.get("temperature_c") is not None: temp     = pico_latest["temperature_c"]
    if pico_latest.get("humidity_rh")   is not None: humidity = pico_latest["humidity_rh"]

# Source indicator
if pico_latest:
    pico_ts = pico_latest.get("ts")
    ts_str  = pd.to_datetime(pico_ts).strftime("%H:%M:%S") if pico_ts else "unknown"
    st.caption(f"🟢 Sensor data — Pico W · last reading at {ts_str}")
else:
    st.caption("🟡 No Pico W data yet — showing OpenWeather fallback")

# ── Metric cards ───────────────────────────────────────────────────────────────
render_metrics_row(temp, humidity, weather, temp_unit=unit)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Live readings (native st.metric) ──────────────────────────────────────────
render_section_header("Live readings")

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Temperature", f"{float(temp):.1f} °C" if temp is not None else "N/A")
with k2:
    st.metric("Humidity", f"{float(humidity):.0f} %" if humidity is not None else "N/A")
with k3:
    st.metric("Light", "N/A", help="Sensor not yet connected")
with k4:
    st.metric("Soil", "N/A", help="Sensor not yet connected")

# ── Charts ─────────────────────────────────────────────────────────────────────
render_section_header("History")

sensor_df  = load_sensor_history(zone="zone1", area="upper_plants", hours=24)
weather_df = load_history(zone="zone1", area="upper_plants", source="openweather", hours=24)

if not sensor_df.empty:
    chart_df     = sensor_df.rename(columns={"temperature_c": "temp_c", "humidity_rh": "humidity_pct"})
    chart_source = "Pico W sensor"
elif not weather_df.empty:
    chart_df     = weather_df
    chart_source = "OpenWeather"
else:
    chart_df     = pd.DataFrame()
    chart_source = None

c1, c2 = st.columns(2)

with c1:
    if not chart_df.empty and "temp_c" in chart_df.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=chart_df["ts"], y=chart_df["temp_c"],
            mode="lines+markers",
            line=dict(color="#10B981", width=2),
            marker=dict(size=5),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            title=f"Temperature °C  ·  {chart_source}",
            xaxis=dict(showgrid=False, tickformat="%H:%M"),
            yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", title="°C"),
            margin=dict(l=0, r=0, t=40, b=0),
            hovermode="x unified", showlegend=False, font=dict(size=11),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No temperature history yet.")

with c2:
    if not chart_df.empty and "humidity_pct" in chart_df.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=chart_df["ts"], y=chart_df["humidity_pct"],
            mode="lines+markers",
            line=dict(color="#3B82F6", width=2, dash="dot"),
            marker=dict(size=5),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            title=f"Humidity %  ·  {chart_source}",
            xaxis=dict(showgrid=False, tickformat="%H:%M"),
            yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", title="%"),
            margin=dict(l=0, r=0, t=40, b=0),
            hovermode="x unified", showlegend=False, font=dict(size=11),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No humidity history yet.")

# ── Soil gauge + Temp vs Humidity overlay ─────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    soil_value = 5.5
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=soil_value,
        title={"text": "Soil Moisture (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar":  {"color": "#10B981", "thickness": 0.3},
            "steps": [
                {"range": [0,  25],  "color": "rgba(239,68,68,0.2)"},
                {"range": [25, 50],  "color": "rgba(245,158,11,0.2)"},
                {"range": [50, 75],  "color": "rgba(16,185,129,0.2)"},
                {"range": [75, 100], "color": "rgba(59,130,246,0.2)"},
            ],
            "threshold": {
                "line":      {"width": 3, "color": "#10B981"},
                "thickness": 0.8,
                "value":     soil_value,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(size=11),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with c4:
    if not chart_df.empty and "temp_c" in chart_df.columns and "humidity_pct" in chart_df.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=chart_df["ts"], y=chart_df["temp_c"],
            mode="lines+markers", name="Temperature (°C)",
            line=dict(color="#10B981", width=2), marker=dict(size=5), yaxis="y1",
        ))
        fig.add_trace(go.Scatter(
            x=chart_df["ts"], y=chart_df["humidity_pct"],
            mode="lines+markers", name="Humidity (%)",
            line=dict(color="#3B82F6", width=2, dash="dash"), marker=dict(size=5), yaxis="y2",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            title=f"Temp vs Humidity  ·  {chart_source}",
            xaxis=dict(showgrid=False, tickformat="%H:%M"),
            yaxis=dict(title="°C", showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
            yaxis2=dict(title="%", overlaying="y", side="right", showgrid=False),
            hovermode="x unified",
            legend=dict(orientation="h", y=1.1, x=0),
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(size=11),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No comparison data available yet.")

# ── Data table ─────────────────────────────────────────────────────────────────
render_section_header("Raw data")

data_source_toggle = st.radio(
    "Data source", ["Pico W sensor", "OpenWeather"],
    horizontal=True, label_visibility="collapsed",
)

show_latest_only = st.toggle("Show latest reading only", value=True)
limit = 1 if show_latest_only else st.slider("Rows", min_value=1, max_value=90, value=20, step=1)

if data_source_toggle == "Pico W sensor":
    docs = load_sensor_readings(zone="zone1", area="upper_plants", limit=limit)
else:
    docs = load_readings(zone="zone1", area="upper_plants", source="openweather", limit=limit)

table_df = pd.DataFrame(docs)
if table_df.empty:
    st.info("No readings found yet.")
else:
    if "ts" in table_df.columns:
        table_df["ts"] = pd.to_datetime(table_df["ts"])
    st.dataframe(table_df, use_container_width=True)

st.markdown("---")