import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.styles import load_css

from utils.db import (
    load_latest,
    load_history,
    load_readings,
)
from utils.zone_config import ZONE1_AREAS, get_area

from utils.layout import (
    render_zone_header,
    render_refresh_update,
    render_metrics_row,
    render_section_header,
    render_zone1_top_controls,
)
from utils.sidebar import render_sidebar
from utils.alerts import get_zone_alert, evaluate_temperature_alert, evaluate_humidity_alert, mark_email_alert_sent, should_send_email_alert
from utils.emailer import send_temperature_alert_email, send_humidity_alert_email

# ── Page config THEN CSS — must happen before any other st calls ───────────────
st.set_page_config(page_title="Zone 1", layout="wide")
load_css()

# ── Apply current theme ────────────────────────────────────────────────────────
# Only zone_text_color is consumed by downstream layout helpers via session_state;
# other theme variables are resolved inside the CSS/layout modules.
if "theme" not in st.session_state:
    st.session_state.theme = "Feeling Green"

from utils.themes import THEMES
import matplotlib.colors as plt
current_theme = THEMES[st.session_state.theme]
text_color = current_theme["text_color"]
zone_text_color = current_theme.get("zone_text_color", text_color)
st.session_state["zone_text_color"] = zone_text_color

render_sidebar()

# ── Header ─────────────────────────────────────────────────────────────────────
render_zone_header("Zone 1")
render_refresh_update()

section, unit = render_zone1_top_controls()

# ── Area selector (one button per collection in ZONE1_AREAS) ──────────────────
if "zone1_area_key" not in st.session_state:
    st.session_state["zone1_area_key"] = ZONE1_AREAS[0]["key"]

render_section_header("Area")
area_cols = st.columns(len(ZONE1_AREAS))
for col, area in zip(area_cols, ZONE1_AREAS):
    is_selected = st.session_state["zone1_area_key"] == area["key"]
    with col:
        if st.button(
            area["label"],
            key=f"area_btn_{area['key']}",
            use_container_width=True,
            type="primary" if is_selected else "secondary",
        ):
            st.session_state["zone1_area_key"] = area["key"]
            st.rerun()

active_area = get_area(ZONE1_AREAS, st.session_state["zone1_area_key"])
active_collection = active_area["collection"]
active_schema     = active_area["schema"]

# ── Data load (single source, driven by active area) ──────────────────────────
latest = load_latest(active_collection, active_schema)

temp     = latest.get("temp_c")       if latest else None
humidity = latest.get("humidity_pct") if latest else None
weather  = latest.get("weather_desc") if latest else None

# Timestamp indicator
if latest and latest.get("ts"):
    ts_str = (
        pd.to_datetime(latest["ts"])
          .tz_localize("UTC")
          .tz_convert("US/Eastern")
          .strftime("%I:%M:%S %p")
    )
    st.caption(f"🟢 {active_area['label']} — last reading at {ts_str}")
else:
    st.caption(f"⚪ {active_area['label']} — no readings found")

# ── Temperature alerts ────────────────────────────────────────────────────────
# TODO: alert logic still keyed on "zone1" and will evaluate whichever area
# button is currently selected against indoor thresholds. Alert rework will
# replace this with per-area evaluation.
zone_alert_settings = get_zone_alert("zone1")
temp_alert = evaluate_temperature_alert(temp, zone="zone1")
humidity_alert = evaluate_humidity_alert(humidity, zone="zone1")
# Use recipient list with fallback to legacy single-recipient key.
email_recipients = zone_alert_settings.get("email_recipients") or []
if not email_recipients and zone_alert_settings.get("email_to"):
    email_recipients = [zone_alert_settings.get("email_to")]
# Collect one or more outbound email results for user visibility.
email_status_msgs = []

# Convert persisted Celsius thresholds for display to match the selected unit.
if unit == "°F":
    threshold_min_display = zone_alert_settings["temp_min_c"] * 9.0 / 5.0 + 32.0
    threshold_max_display = zone_alert_settings["temp_max_c"] * 9.0 / 5.0 + 32.0
else:
    threshold_min_display = zone_alert_settings["temp_min_c"]
    threshold_max_display = zone_alert_settings["temp_max_c"]

if temp is None:
    st.warning("Temperature alert status unavailable because no current temperature reading was found.")
elif not zone_alert_settings.get("enabled", True):
    st.info("Temperature alerts are currently disabled for Zone 1. Enable them in Settings.")
elif temp_alert and temp_alert["kind"] == "low":
    # Alert values are stored/evaluated in Celsius and converted only for UI output.
    alert_temp_display = temp_alert["temp_c"] * 9.0 / 5.0 + 32.0 if unit == "°F" else temp_alert["temp_c"]
    alert_threshold_display = temp_alert["threshold_c"] * 9.0 / 5.0 + 32.0 if unit == "°F" else temp_alert["threshold_c"]
    st.error(
        f"Low temperature alert: {alert_temp_display:.1f} {unit} is below "
        f"the minimum threshold ({alert_threshold_display:.1f} {unit})."
    )
    if zone_alert_settings.get("email_enabled", False) and email_recipients:
        cooldown = int(zone_alert_settings.get("email_cooldown_minutes", 30))
        # Cooldown is metric-specific so humidity emails do not block temperature emails.
        if should_send_email_alert("zone1", "low", cooldown_minutes=cooldown, metric="temperature"):
            sent_any = False
            # Send to each configured recipient and aggregate per-address status.
            for recipient in email_recipients:
                ok, msg = send_temperature_alert_email(
                    recipient=recipient,
                    zone="zone1",
                    kind="low",
                    temp_c=float(temp_alert["temp_c"]),
                    threshold_c=float(temp_alert["threshold_c"]),
                )
                sent_any = sent_any or ok
                email_status_msgs.append(f"{recipient}: {msg}")
            if sent_any:
                mark_email_alert_sent("zone1", "low", metric="temperature")
elif temp_alert and temp_alert["kind"] == "high":
    alert_temp_display = temp_alert["temp_c"] * 9.0 / 5.0 + 32.0 if unit == "°F" else temp_alert["temp_c"]
    alert_threshold_display = temp_alert["threshold_c"] * 9.0 / 5.0 + 32.0 if unit == "°F" else temp_alert["threshold_c"]
    st.error(
        f"High temperature alert: {alert_temp_display:.1f} {unit} exceeds "
        f"the maximum threshold ({alert_threshold_display:.1f} {unit})."
    )
    if zone_alert_settings.get("email_enabled", False) and email_recipients:
        cooldown = int(zone_alert_settings.get("email_cooldown_minutes", 30))
        if should_send_email_alert("zone1", "high", cooldown_minutes=cooldown, metric="temperature"):
            sent_any = False
            for recipient in email_recipients:
                ok, msg = send_temperature_alert_email(
                    recipient=recipient,
                    zone="zone1",
                    kind="high",
                    temp_c=float(temp_alert["temp_c"]),
                    threshold_c=float(temp_alert["threshold_c"]),
                )
                sent_any = sent_any or ok
                email_status_msgs.append(f"{recipient}: {msg}")
            if sent_any:
                mark_email_alert_sent("zone1", "high", metric="temperature")
else:
    st.success(
        f"Temperature is within range ({threshold_min_display:.1f} to "
        f"{threshold_max_display:.1f} {unit})."
    )

# ── Humidity alerts ───────────────────────────────────────────────────────────
humidity_min = float(zone_alert_settings.get("humidity_min_pct", 45.0))
humidity_max = float(zone_alert_settings.get("humidity_max_pct", 80.0))

if humidity is None:
    st.warning("Humidity alert status unavailable because no current humidity reading was found.")
elif not zone_alert_settings.get("enabled", True):
    st.info("Humidity alerts are currently disabled for Zone 1. Enable them in Settings.")
elif humidity_alert and humidity_alert["kind"] == "low":
    st.error(
        f"Low humidity alert: {humidity_alert['humidity_pct']:.0f}% is below "
        f"the minimum threshold ({humidity_alert['threshold_pct']:.0f}%)."
    )
    if zone_alert_settings.get("email_enabled", False) and email_recipients:
        cooldown = int(zone_alert_settings.get("email_cooldown_minutes", 30))
        if should_send_email_alert("zone1", "low", cooldown_minutes=cooldown, metric="humidity"):
            sent_any = False
            # Send to each configured recipient and aggregate per-address status.
            for recipient in email_recipients:
                ok, msg = send_humidity_alert_email(
                    recipient=recipient,
                    zone="zone1",
                    kind="low",
                    humidity_pct=float(humidity_alert["humidity_pct"]),
                    threshold_pct=float(humidity_alert["threshold_pct"]),
                )
                sent_any = sent_any or ok
                email_status_msgs.append(f"{recipient}: {msg}")
            if sent_any:
                mark_email_alert_sent("zone1", "low", metric="humidity")
elif humidity_alert and humidity_alert["kind"] == "high":
    st.error(
        f"High humidity alert: {humidity_alert['humidity_pct']:.0f}% exceeds "
        f"the maximum threshold ({humidity_alert['threshold_pct']:.0f}%)."
    )
    if zone_alert_settings.get("email_enabled", False) and email_recipients:
        cooldown = int(zone_alert_settings.get("email_cooldown_minutes", 30))
        if should_send_email_alert("zone1", "high", cooldown_minutes=cooldown, metric="humidity"):
            sent_any = False
            for recipient in email_recipients:
                ok, msg = send_humidity_alert_email(
                    recipient=recipient,
                    zone="zone1",
                    kind="high",
                    humidity_pct=float(humidity_alert["humidity_pct"]),
                    threshold_pct=float(humidity_alert["threshold_pct"]),
                )
                sent_any = sent_any or ok
                email_status_msgs.append(f"{recipient}: {msg}")
            if sent_any:
                mark_email_alert_sent("zone1", "high", metric="humidity")
else:
    st.success(f"Humidity is within range ({humidity_min:.0f}% to {humidity_max:.0f}%).")

for msg in email_status_msgs:
    # Show send outcomes (success/failure) directly below alerts.
    st.caption(msg)

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

# --- Load history from the active collection only ---
chart_df = load_history(
    active_collection,
    active_schema,
    hours=hours,
    start_ts=start_time,
    end_ts=end_time,
)
chart_source = active_area["label"]

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

show_latest_only = st.toggle("Show latest reading only", value=True)
limit = 1 if show_latest_only else st.slider("Rows", min_value=1, max_value=90, value=20, step=1)

docs = load_readings(active_collection, active_schema, limit=limit)

table_df = pd.DataFrame(docs)
if table_df.empty:
    st.info("No readings found yet.")
else:
    if "ts" in table_df.columns:
        # Convert table timestamps to Eastern Time
        table_df["ts"] = pd.to_datetime(table_df["ts"]).dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    st.dataframe(table_df, use_container_width=True)

st.markdown("---")