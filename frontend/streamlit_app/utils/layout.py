import os
import sys
from datetime import datetime
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
import textwrap
import base64

import streamlit as st
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px





#header function title
def render_zone_header(zone_name: str):
    st.title(f"Zone {zone_name}")
    st.sidebar.caption(f"Zone {zone_name} navigation")

#redering last time update app
def render_refresh_update():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"Last updated: {now}")

    if st.button("Refresh"):
        st.session_state["last_update"] = datetime.now()

    if "last_update" in st.session_state:
        st.caption(
            "Last updated: " +
            st.session_state["last_update"].strftime("%Y-%m-%d %H:%M:%S")
        )

def render_api_update():
    # find .env next to streamlit_app
    env_path = Path(__file__).resolve().parents[1] / ".env"

   ## st.write("Looking for .env at:", str(env_path))
    st.write(".env exists:", env_path.exists())

    load_dotenv(dotenv_path=env_path, override=True)

    api_key = os.getenv("OPENWEATHER_API_KEY")
    st.write("API key loaded:", bool(api_key))

    if api_key:
        st.write("API key length:", len(api_key))
        st.code(api_key[:4] + "..." + api_key[-4:])
    else:
        st.write("API key not loaded")




ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
def load_icon_b64(filename: str) -> str:
    path = ASSETS_DIR / filename
    return base64.b64encode(path.read_bytes()).decode("utf-8")


# Load icons once
TEMP_ICON = load_icon_b64("temperature.png")
HUMIDITY_ICON = load_icon_b64("humidity.png")
SOIL_MOISTURE_ICON = load_icon_b64("soil.png")

def render_zone_header(zone_name: str):
    st.title(f"🌱 {zone_name}")
    st.sidebar.caption(f"{zone_name} navigation")

def render_zone1_top_controls():
        if "zone1_section" not in st.session_state:
            st.session_state["zone1_section"] = "Upper Plants"

        if "temp_unit" not in st.session_state:
            st.session_state["temp_unit"] = "°C"

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

        st.divider()

        col_controls, col_alerts = st.columns(2)

        with col_controls:
            with st.container(border=True):
                st.markdown("#### ⚙️ Controls")
                unit = st.radio(
                    "Temperature Unit",
                    ["°C", "°F"],
                    horizontal=True,
                    label_visibility="collapsed",
                    key="temp_unit"
                )

        with col_alerts:
            with st.container(border=True):
                st.markdown("#### 🚨 Upper Section Alerts")
                st.write("Coming soon…")

        section = st.session_state["zone1_section"]
        return section, unit


def render_metric_box(title, value, color, icon=None):
    icon_html = ""
    if icon:
        icon_html = f'<img src="data:image/png;base64,{icon}" style="width:40px;height:40px;">'

    html = f"""
    <div style="
        background-color: {color};
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.12);
        color: white;
    ">
      <div style="
          font-size: 30px;
          font-weight: 700;
          margin-bottom: 10px;
          display: flex;
          align-items: center;
          gap: 8px;
      ">
        {icon_html}
        <span>{title}</span>
      </div>

      <div style="
          font-size: 32px;
          font-weight: 800;
      ">
        {value}
      </div>
    </div>
    """
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)


# --------------------------------------------------
# Metrics Layout (4 columns)
# --------------------------------------------------

def render_metrics_row(temp, humidity, weather):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_box(
            "Temperature",
            f"{float(temp):.1f}°C" if temp is not None else "N/A",
            "#131b59",
            TEMP_ICON
        )

    with col2:
        render_metric_box(
            "Humidity",
            f"{humidity}%" if humidity is not None else "N/A",
            "#edaf10",
            HUMIDITY_ICON
        )

    with col3:
        render_metric_box(
            "Weather 🌤️",
            str(weather).capitalize() if weather is not None else "N/A",
            "#57360b"
        )

    with col4:
        render_metric_box(
            "Soil Moisture",
            "5.5%",
            "#2e6b3e",
            SOIL_MOISTURE_ICON
        )

def render_section_header(title: str, icon: str | None = None):
    icon_html = ""
    if icon:
        icon_html = (
            f'<img src="data:image/png;base64,{icon}" '
            f'style="width:70px;height:70px;object-fit:contain;">'
        )

    html = f"""
    <div style="
        display:flex;
        justify-content:center;
        align-items:center;
        gap:14px;
        margin:35px 0 10px 0;
    ">
        {icon_html}
        <h2 style="
            margin:0;
            font-weight:500;
            letter-spacing:0.5px;
        ">
            {title}
        </h2>
    </div>

    <div style="
        width:120px;
        height:3px;
        background-color:#1f77b4;
        margin:10px auto 25px auto;
        border-radius:2px;
    "></div>
    """


    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)
def load_icon_b64(filename: str) -> str:
    path = ASSETS_DIR / filename
    return base64.b64encode(path.read_bytes()).decode("utf-8")


# Existing icons
TEMP_ICON = load_icon_b64("temperature.png")
HUMIDITY_ICON = load_icon_b64("humidity.png")
SOIL_MOISTURE_ICON = load_icon_b64("soil.png")
HANGING_ICON = load_icon_b64("hanging-pot.png")



import streamlit as st


def dashboard_title_metric_section():
    st.markdown(
        """
        <style>
        /* Metric label */
        [data-testid="stMetricLabel"]{
            font-size: 18px !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px !important;
            color: #9CA3AF !important;
            text-transform: uppercase !important;
        }

        [data-testid="stMetricLabel"] p{
            margin-bottom: 6px !important;
        }

        /* Metric value */
        [data-testid="stMetricValue"]{
            font-size: 38px !important;
            font-weight: 800 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


