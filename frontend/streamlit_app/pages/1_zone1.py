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

# ── Apply current theme ────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "Feeling Green"

if True:
    from utils.themes import THEMES
    import matplotlib.colors as plt
    current_theme = THEMES[st.session_state.theme]
    background_color = plt.XKCD_COLORS[current_theme["background"]]
    sidebar_color = plt.XKCD_COLORS[current_theme["sidebar"]]
    title_color = plt.XKCD_COLORS[current_theme["title"]]
    boxes_color = plt.XKCD_COLORS[current_theme["boxes"]]
    top_bar_color = plt.XKCD_COLORS[current_theme["top_bar"]]
    text_color = current_theme["text_color"]
    title_text_color = current_theme.get("title_text_color", text_color)
    caption_color = current_theme.get("caption_color", text_color)
    zone_text_color = current_theme.get("zone_text_color", text_color)

    # helper to resolve color
    def _resolve_color(value):
        if isinstance(value, str) and value.startswith("xkcd:"):
            return plt.XKCD_COLORS[value]
        return value

    subtitle_color = _resolve_color(current_theme.get("subtitle", current_theme["text_color"]))

    # Set theme variables
    st.markdown(f"""
    <style>
    :root {{
        --background-color: {background_color};
        --sidebar-color: {sidebar_color};
        --title-color: {title_color};
        --boxes-color: {boxes_color};
        --top-bar-color: {top_bar_color};
        --text-color: {text_color};
        --subtitle-color: {subtitle_color};
        --secondary-background-color: {boxes_color};
        --title-text-color: {title_text_color};
        --caption-color: {caption_color};
        --zone-text-color: {zone_text_color};
    }}
    
    /* Zone 1 text color overrides - universal */
    /* Apply white text to ALL elements on the page */
    * {{
        color: {zone_text_color} !important;
    }}
    
    /* Specifically target markdown and text content */
    [data-testid="stMarkdown"] {{
        color: {zone_text_color} !important;
    }}
    
    [data-testid="stCaption"] {{
        color: {zone_text_color} !important;
    }}
    
    [data-testid="stCaption"] * {{
        color: {zone_text_color} !important;
    }}
    
    [data-testid="stCaption"] p,
    [data-testid="stCaption"] span,
    [data-testid="stCaption"] small {{
        color: {zone_text_color} !important;
    }}
    
    /* Force white on all text elements - override inline styles */
    [style*="color"] {{
        color: {zone_text_color} !important;
    }}
    
    /* Force white on small text and captions */
    small {{
        color: {zone_text_color} !important;
    }}
    
    /* Target elements by their tag names more aggressively */
    p {{
        color: {zone_text_color} !important;
    }}
    
    span {{
        color: {zone_text_color} !important;
    }}
    
    /* Override any specific page classes */
    .page-title,
    .page-subtitle {{
        color: {zone_text_color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Store theme color in session state for layout functions
    st.session_state["zone_text_color"] = zone_text_color

render_sidebar()

# ── Header ─────────────────────────────────────────────────────────────────────
render_zone_header("Zone 1")
render_refresh_update()

section, unit = render_zone1_top_controls()

# ── Data sources ───────────────────────────────────────────────────────────────
# Priority: Pico W (inside greenhouse) > OpenWeather mongo > live API fallback

pico_latest  = load_latest_sensor(zone="zone1", area="upper_plants")
mongo_latest = load_latest_reading(zone="zone1", area="upper_plants", source="zone1_dht22_test")
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
    # Convert UTC to US/Eastern
    if pico_ts:
        ts_str = pd.to_datetime(pico_ts).tz_localize('UTC').tz_convert('US/Eastern').strftime("%I:%M:%S %p")
    else:
        ts_str = "unknown"
    st.caption(f"🟢 Sensor data — Pico W · last reading at {ts_str}")

# ── Metric cards ───────────────────────────────────────────────────────────────
render_metrics_row(temp, humidity, weather, temp_unit=unit)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Live readings (native st.metric) ──────────────────────────────────────────
render_section_header("Live readings")

if temp is not None:
    display_temp = (temp * 9/5) + 32 if unit == "°F" else temp
    temp_string = f"{float(display_temp):.1f} {unit}"
else:
    temp_string = "N/A"

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Temperature", temp_string)
with k2:
    st.metric("Humidity", f"{float(humidity):.0f} %" if humidity is not None else "N/A")
with k3:
    st.metric("Light", "N/A", help="Sensor not yet connected")
# ── Charts ─────────────────────────────────────────────────────────────────────
render_section_header("History")

st.markdown("**Filter Data Range**")
col_radio, col_date = st.columns([1, 2])

with col_radio:
    time_mode = st.radio("Range Type", ["Last 24 Hours", "Last 7 Days", "Custom Range"], label_visibility="collapsed")

start_time = None
end_time = None
hours = 24

with col_date:
    if time_mode == "Last 24 Hours":
        hours = 24
    elif time_mode == "Last 7 Days":
        hours = 168 # 24 * 7
    else:
        # Custom Range: Date Picker
        today = pd.Timestamp.now('US/Eastern').date()
        date_range = st.date_input("Select Date Range", (today - pd.Timedelta(days=2), today))
        
        # Only show time pickers IF they have successfully selected a start and end date
        if len(date_range) == 2:
            # Create two small columns for the time pickers
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                start_t = st.time_input("Start Time", value=pd.Timestamp('00:00:00').time())
            with t_col2:
                end_t = st.time_input("End Time", value=pd.Timestamp('23:59:59').time())
            
            # 1. Combine the selected Date + Time into a single Pandas datetime object
            start_combined = pd.to_datetime(f"{date_range[0]} {start_t}")
            end_combined = pd.to_datetime(f"{date_range[1]} {end_t}")
            
            # 2. Assign the Eastern timezone, then convert to UTC for the database!
            start_time = start_combined.tz_localize('US/Eastern').tz_convert('UTC').to_pydatetime()
            end_time = end_combined.tz_localize('US/Eastern').tz_convert('UTC').to_pydatetime()
            hours = None # Turn off the "hours" fallback

# --- PASS THE NEW FILTERS INTO THE DATABASE ---
sensor_df  = load_sensor_history(zone="zone1", area="upper_plants", hours=hours, start_ts=start_time, end_ts=end_time)
weather_df = load_history(zone="zone1", area="upper_plants", source="zone1_dht22_test", hours=hours, start_ts=start_time, end_ts=end_time)


if not sensor_df.empty:
    chart_df     = sensor_df.rename(columns={"temperature_c": "temp_c", "humidity_rh": "humidity_pct"})
    chart_source = "Pico W sensor"
elif not weather_df.empty:
    chart_df     = weather_df
    chart_source = "OpenWeather"
else:
    chart_df     = pd.DataFrame()
    chart_source = None

if not chart_df.empty and "ts" in chart_df.columns:
    chart_df["ts"] = pd.to_datetime(chart_df["ts"]).dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    
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

# ── Temp vs Humidity overlay (full width) ─────────────────────────────────────
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
        
        # 1. Move legend below the x-axis, centered
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        
        # 2. Add 40px of bottom margin (b=40) so the legend doesn't get cut off
        margin=dict(l=0, r=0, t=50, b=40),
        
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
    docs = load_readings(zone="zone1", area="upper_plants", source="zone1_dht22_test", limit=limit)

table_df = pd.DataFrame(docs)
if table_df.empty:
    st.info("No readings found yet.")
else:
    if "ts" in table_df.columns:
        # Convert table timestamps to Eastern Time
        table_df["ts"] = pd.to_datetime(table_df["ts"]).dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    st.dataframe(table_df, use_container_width=True)

st.markdown("---")