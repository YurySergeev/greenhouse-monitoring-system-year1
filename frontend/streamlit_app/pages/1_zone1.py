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
import matplotlib.colors as plt

#--------------------------- charts libraries
import plotly.express as px
import plotly.graph_objects as go #gauge chart

#----------------------------- database down here
from pymongo import MongoClient
from dotenv import load_dotenv
#-------------------------------

# Define themes (same as Home.py)
THEMES = {
    "Earth Day Vibes": {
        "background": "xkcd:greenish grey",
        "sidebar": "xkcd:coffee",
        "title": "xkcd:coffee",
        "boxes": "xkcd:coffee",
        "top_bar": "xkcd:coffee",
        "text_color": "#ffffff"
    },
    "Feeling Green": {
        "background": "xkcd:greenish grey",
        "sidebar": "xkcd:dark sage",
        "title": "xkcd:dark sage",
        "boxes": "xkcd:dark sage",
        "top_bar": "xkcd:dark sage",
        "text_color": "#ffffff"
    },
    "Go Flashes!": {
        "background": "xkcd:white",
        "sidebar": "xkcd:blue",
        "title": "xkcd:blue",
        "boxes": "xkcd:blue",
        "top_bar": "xkcd:blue",
        "text_color": "#ffd700"
    }
}

# Initialize session state for theme
if "theme" not in st.session_state:
    st.session_state.theme = "Earth Day Vibes"

from dotenv import load_dotenv, find_dotenv

# Get current theme colors
current_theme = THEMES[st.session_state.theme]
background_color = plt.XKCD_COLORS[current_theme["background"]]
sidebar_color = plt.XKCD_COLORS[current_theme["sidebar"]]
title_color = plt.XKCD_COLORS[current_theme["title"]]
boxes_color = plt.XKCD_COLORS[current_theme["boxes"]]
top_bar_color = plt.XKCD_COLORS[current_theme["top_bar"]]
text_color = current_theme["text_color"]
top_bar_color = plt.XKCD_COLORS[current_theme["top_bar"]]
from dotenv import load_dotenv, find_dotenv

# ----- frontend/assets/css
from pathlib import Path
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

# ----------------------------
# Icons (keep your get_icon)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TEMP_ICON = get_icon("temperature.png")
HUMIDITY_ICON = get_icon("humidity.png")
SOIL_MOISTURE_ICON = get_icon("soil.png")
HANGING_POT_ICON = get_icon("hanging-pot.png")
GROUND_PLANTS_ICON = get_icon("ground_plants.png")


# ----------------------------
# Hide page from sidebar (your CSS)
# ----------------------------

# Hide page from sidebar
st.markdown(f"""
    <style>
    :root {{
        --background-color: {background_color};
        --top-bar-color: {top_bar_color};
        --sidebar-color: {sidebar_color};
    }}
    /* ----------------------------
     Hide page from sidebar (your CSS)
     ---------------------------- */
    /* Hide only the second page (zone1) */
    [data-testid="stSidebarNav"] ul li:nth-child(2) {{
        display: none;
    }}
    
    /* Apply theme colors */
    .stApp {{
        background-color: var(--background-color);
    }}
    
    [data-testid="stHeader"] {{
        background-color: var(--top-bar-color);
    }}
    
    .stSidebar {{
        background-color: var(--sidebar-color);
    }}
    .stRadio label {{
        color: var(--text-color) !important;
    }}
    .stRadio span {{
        color: var(--text-color) !important;
    }}
    .stRadio div {{
        color: var(--text-color) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Zones", layout="wide")
st.markdown(f"<h1 style='color: {text_color};'>Zone 1 General metrics</h1>", unsafe_allow_html=True)
st.sidebar.caption("Zone 1 navigation")




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
            st.markdown(f"""
            <div style="background-color: {sidebar_color}; padding: 10px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.12);">
            <h4 style="color: {text_color};">⚙️ Controls</h4>
            """, unsafe_allow_html=True)
            unit = st.radio("Temperature Unit", ["°C", "°F"], horizontal=True, label_visibility="collapsed",
                            key="temp_unit")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_alerts:
            st.markdown(f"""
            <div style="background-color: {sidebar_color}; padding: 10px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.12);">
            <h4 style="color: {text_color};">🚨 Upper Section Alerts</h4>
            <p style="color: {text_color};">Coming soon…</p>
            </div>
            """, unsafe_allow_html=True)


        return section, unit

    return section, None


        # upper_plntas_func() #here will live dashboards for upper plants




def main():
    section, unit = sidebar_control_func()

    st.markdown(f"<h1 style='color: {text_color};'>Zone 1 Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {text_color};'>Selected: <strong>{section}</strong></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {text_color};'>Unit: {unit}</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()




# Theme selector in sidebar (bottom left)
st.sidebar.divider()
if st.sidebar.button("🌿 Change Theme", key="theme_button", help="Cycle through themes", use_container_width=True):
    # Cycle through themes
    themes_list = list(THEMES.keys())
    current_index = themes_list.index(st.session_state.theme)
    next_index = (current_index + 1) % len(themes_list)
    st.session_state.theme = themes_list[next_index]
    st.rerun()

# Last updated timestamp (only once)
st.markdown(f"<small style='color: {text_color};'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>", unsafe_allow_html=True)

# Debug: confirm env loaded
st.markdown(f"<p style='color: {text_color};'>API Key {bool(API_KEY)}</p>", unsafe_allow_html=True)
st.markdown(f"<p style='color: {text_color};'>API key length: {len(API_KEY) if API_KEY else None}</p>", unsafe_allow_html=True)
st.markdown(f"<p style='color: {text_color};'>API key preview: {(API_KEY[:4] + '...' + API_KEY[-4:]) if API_KEY else None}</p>", unsafe_allow_html=True)

# ----------------------------
# Weather: OpenWeather (cached to avoid 429)
# ---------------------------
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=300_000, key="refresh_5min")  # 5 minutes


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



def weaather_conditions_func():
    weather_images = {
        "Mist": ""
    }


# ----------------------------
# Metric cards HTML
# ----------------------------
def metric_box_style(title, value, color, icon=None):
    icon_html = ""
    if icon:
        icon_html = f'<img src="data:image/png;base64,{icon}" style="width:40px;height:40px;">'

    html = f"""
    <div style="
        background-color: {color};
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.12);
        color: {text_color};
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

# ----------------------------
# Layout / Display
# ----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    if temp is not None:
        metric_box_style("Temperature", f"{float(temp):.1f}°C", sidebar_color, TEMP_ICON)
    else:
        metric_box_style("Temperature", "N/A", sidebar_color, TEMP_ICON)

with col2:
    if humidity is not None:
        metric_box_style("Humidity", f"{humidity}%", sidebar_color, HUMIDITY_ICON)
    else:
        metric_box_style("Humidity", "N/A", sidebar_color, HUMIDITY_ICON)

with col3:
    if weather is not None:
        metric_box_style("Weather 🌤️", str(weather).capitalize(), sidebar_color)
    else:
        metric_box_style("Weather 🌤️", "N/A", sidebar_color)

with col4:
    metric_box_style("Soil Moisture", "5.5%", sidebar_color, SOIL_MOISTURE_ICON)


####### SECTION HEASDER FOR HANGING PLANTS #############
import textwrap

def section_header_function(title: str, icon=None):
    icon_html = ""
    if icon:
        icon_html = (f'<img src="data:image/png;base64,{icon}" '
                     f'style="width:70px;'
                     f'height:70px;'
                     f'object-fit:contain;">')

    html = f"""
<div style="display:flex;justify-content:center;
align-items:center;
gap:14px;
margin:35px 0 10px 0;">{icon_html}
  <h2 style="margin:0;
  font-weight:500;
  letter-spacing:0.5px;">{title}</h2>

</div>

<div style="width:120px;height:3px;background-color:#1f77b4;margin:10px auto 25px auto;border-radius:2px;"></div>
"""
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)




#metrics label style -----------------------
st.markdown("""
<style>
[data-testid="stMetricLabel"]{
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #9CA3AF;
    text-transform: uppercase;
}
[data-testid="stMetricLabel"] p{
    margin-bottom: 6px;
}
[data-testid="stMetricValue"]{
    font-size: 38px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)
# -----------------------------------------------

UPPER_ZONE_RULES = {
    "temp" : {"low": 18.0, "high": 25.0},
    "humidity" : { "low": 45.0, "high": 75.0},
    "light" : {"low" : 600.0, "high": 1200.0},
    "soil" : {"low": 25.0, "high": 45.0 },
}

def metric_in_range(label, value, low, high, unit=""):
    #in range will show ok, green pill
    '''
    if low <= value <= high:
        st.metric(label, f"{value:.1f}{unit}", "Within range", delta_color="normal")
        return

        #  below range, read pill
    if value < low:
        diff = value - low  # negative
        st.metric(label, f"{value:.1f}{unit}", f"{diff:+.1f}{unit} Extreme Condition", delta_color="normal")
        return

        #  above range, red pill
    diff = value - high  # positive
    st.metric(label, f"{value:.1f}{unit}", f"{diff:+.1f}{unit} above max", delta_color="inverse")
    '''


# ---------------------------
# UPPER PLANTS (Zone 1)
# ---------------------------
import os
import pandas as pd
import streamlit as st
from pymongo import MongoClient
import plotly.express as px
import plotly.graph_objects as go

ZONE = "zone1"
AREA = "upper_plants"
SOURCE = "openweather"   # IMPORTANT: matches your inserted docs

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

# ---- Section header ----
section_header_function("Upper Plants", HANGING_POT_ICON)

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





