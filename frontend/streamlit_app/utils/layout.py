import os
import sys
from datetime import datetime
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
import base64

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


# --------------------------------------------------
# Asset loading
# --------------------------------------------------

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"

@st.cache_data
def load_icon_b64(filename: str) -> str:
    path = ASSETS_DIR / filename
    return base64.b64encode(path.read_bytes()).decode("utf-8")


# --------------------------------------------------
# Page header
# --------------------------------------------------

def render_zone_header(zone_name: str):
    """Renders the top page title with a live badge."""
    st.markdown(f"""
    <div class="page-header">
        <div>
            <p class="page-title">{zone_name}</p>
            <p class="page-subtitle">Real-time environmental monitoring</p>
        </div>
        <div class="live-badge">
            <div class="live-badge-dot"></div>
            Live
        </div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# Last updated / refresh
# --------------------------------------------------

def render_refresh_update():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    col_time, col_btn = st.columns([5, 1])
    with col_time:
        st.caption(f"Last synced: {now}")
    with col_btn:
        if st.button("Refresh", use_container_width=True):
            st.session_state["last_update"] = datetime.now()
            st.cache_data.clear()
            st.rerun()


# --------------------------------------------------
# Zone 1 sub-section nav + controls
# --------------------------------------------------

def render_zone1_top_controls():
    if "zone1_section" not in st.session_state:
        st.session_state["zone1_section"] = "Upper Plants"
    if "temp_unit" not in st.session_state:
        st.session_state["temp_unit"] = "°C"

    # Sub-section buttons
    col1, col2, col3, col_spacer = st.columns([1, 1, 1, 3])
    with col1:
        if st.button("Upper Plants", use_container_width=True):
            st.session_state["zone1_section"] = "Upper Plants"
    with col2:
        if st.button("Middle Plants", use_container_width=True):
            st.session_state["zone1_section"] = "Middle Plants"
    with col3:
        if st.button("Ground Plants", use_container_width=True):
            st.session_state["zone1_section"] = "Ground Plants"

    st.divider()

    col_controls, col_alerts = st.columns(2)

    with col_controls:
        with st.container(border=True):
            st.markdown("**Temperature unit**")
            unit = st.radio(
                "Temperature Unit",
                ["°C", "°F"],
                horizontal=True,
                label_visibility="collapsed",
                key="temp_unit",
            )

    with col_alerts:
        with st.container(border=True):
            st.markdown("**Alerts**")
            st.caption("No active alerts — all sensors nominal.")

    section = st.session_state["zone1_section"]
    return section, unit


# --------------------------------------------------
# Individual metric card
# --------------------------------------------------

def render_metric_card(title: str, value: str, chip_class: str, icon: str, trend: str = "", trend_class: str = ""):
    trend_html = ""
    if trend:
        trend_html = f'<div class="metric-trend {trend_class}">{trend}</div>'

    html = f"""
    <div class="metric-card">
        <div class="metric-icon-chip {chip_class}">{icon}</div>
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        {trend_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# --------------------------------------------------
# Metrics row (4 cards)
# --------------------------------------------------

def render_metrics_row(temp, humidity, weather, temp_unit="°C"):
    # Convert if needed
    if temp is not None:
        temp_f = round(temp * 9 / 5 + 32, 1)
        display_temp = f"{float(temp):.1f}<span class='metric-unit'>°C</span>" if temp_unit == "°C" \
                       else f"{temp_f}<span class='metric-unit'>°F</span>"
    else:
        display_temp = "N/A"

    display_humidity = f"{humidity}<span class='metric-unit'>%</span>" if humidity is not None else "N/A"
    display_weather  = str(weather).title() if weather is not None else "N/A"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card(
            title="Temperature",
            value=display_temp,
            chip_class="chip-green",
            icon="🌡️",
            trend="↑ 0.3° from 1h ago",
            trend_class="trend-up",
        )

    with col2:
        render_metric_card(
            title="Humidity",
            value=display_humidity,
            chip_class="chip-blue",
            icon="💧",
            trend="— stable",
        )

    with col3:
        render_metric_card(
            title="Soil Moisture",
            value="5.5<span class='metric-unit'>%</span>",
            chip_class="chip-amber",
            icon="🪴",
            trend="↓ low — check soon",
            trend_class="trend-warn",
        )

    with col4:
        render_metric_card(
            title="Weather",
            value=f'<span style="font-size:18px;font-weight:500;color:#374151;">{display_weather}</span>',
            chip_class="chip-gray",
            icon="🌤️",
            trend="Akron, OH",
        )

    # breathing room below cards
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# --------------------------------------------------
# Section header (title + green underline)
# --------------------------------------------------

def render_section_header(title: str, icon: str | None = None):
    icon_html = f'<span style="font-size:18px;">{icon}</span>' if icon else ""

    html = f"""
    <div>
        <div class="section-title-container">
            {icon_html}
            <h2 class="section-title">{title}</h2>
        </div>
        <div class="section-divider"></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# --------------------------------------------------
# 24-hour trend chart (Plotly)
# --------------------------------------------------

def render_trend_chart(df: pd.DataFrame):
    """Renders a clean temperature & humidity line chart from a history dataframe."""
    if df is None or df.empty:
        st.info("No history data available yet.")
        return

    fig = go.Figure()

    # Temperature line
    fig.add_trace(go.Scatter(
        x=df["ts"],
        y=df["temp_c"],
        name="Temperature (°C)",
        line=dict(color="#10B981", width=2),
        hovertemplate="%{y:.1f}°C<extra></extra>",
    ))

    # Humidity line
    fig.add_trace(go.Scatter(
        x=df["ts"],
        y=df["humidity_pct"],
        name="Humidity (%)",
        line=dict(color="#3B82F6", width=2, dash="dot"),
        yaxis="y2",
        hovertemplate="%{y}%<extra></extra>",
    ))

    fig.update_layout(
        height=220,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#6B7280"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11),
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickformat="%H:%M",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F3F4F6",
            zeroline=False,
            title="°C",
            titlefont=dict(size=10),
        ),
        yaxis2=dict(
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False,
            title="%",
            titlefont=dict(size=10),
        ),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# --------------------------------------------------
# Zone health panel (progress bars)
# --------------------------------------------------

def render_zone_health(temp, humidity):
    """Simple health summary with inline progress bars."""

    def _health_row(label: str, pct: int, status: str, color: str):
        bar_color = {"good": "#10B981", "warn": "#F59E0B", "bad": "#EF4444"}.get(color, "#10B981")
        status_color = {"good": "#065F46", "warn": "#92400E", "bad": "#991B1B"}.get(color, "#065F46")
        status_bg   = {"good": "#D1FAE5", "warn": "#FEF3C7", "bad": "#FEE2E2"}.get(color, "#D1FAE5")

        return f"""
        <div style="margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
                <span style="font-size:12px;color:#374151;">{label}</span>
                <span style="font-size:11px;font-weight:600;color:{status_color};background:{status_bg};
                             padding:2px 8px;border-radius:20px;">{status}</span>
            </div>
            <div style="height:4px;background:#F3F4F6;border-radius:2px;">
                <div style="height:4px;width:{pct}%;background:{bar_color};border-radius:2px;"></div>
            </div>
        </div>
        """

    temp_pct  = min(int((temp / 35) * 100), 100) if temp is not None else 0
    hum_pct   = int(humidity) if humidity is not None else 0

    temp_color  = "good" if 18 <= (temp or 0) <= 28 else "warn"
    hum_color   = "good" if 50 <= (humidity or 0) <= 80 else "warn"

    html = f"""
    <div style="padding:4px 0;">
        {_health_row("Temperature", temp_pct,  "Good" if temp_color == "good" else "High", temp_color)}
        {_health_row("Humidity",    hum_pct,   "Good" if hum_color  == "good" else "Low",  hum_color)}
        {_health_row("Soil moisture", 20,      "Low", "bad")}
        {_health_row("Sensor uptime", 99,      "99.2%", "good")}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)