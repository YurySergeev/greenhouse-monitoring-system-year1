from urllib import response
import streamlit as st
from datetime import datetime, timedelta
import os
from streamlit import subheader
import requests
import time
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

#-------------------------------------------------------------------



BASE_DIR = os.path.dirname(os.path.dirname(__file__))


TEMP_ICON = get_icon("temperature.png")
HUMIDITY_ICON = get_icon("humidity.png")
SOIL_MOISTURE_ICON = get_icon("soil.png")
HANGING_POT_ICON = get_icon("hanging-pot.png")


# Hide page from sidebar
st.markdown(
    """
    <style>
    /* Hide only the second page (zone1) */
    [data-testid="stSidebarNav"] ul li:nth-child(2) {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Zones", layout="wide")
st.title("Zone 1 General metrics")
st.sidebar.caption("Zone 1 navigation")

# Sidebar for zone 1
zone1_selection = st.sidebar.selectbox(
    "Select a metric for zone 1",
    ["Dashboard", "Analytics", "Zone 1 Alerts"],
    index=0
)

# Last updated timestamp (only once)
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load environment variables
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)
API_KEY = os.getenv("OPENWEATHER_API_KEY")

st.write("API Key", bool(API_KEY))

CITY = "Akron"
url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&units=imperial&appid={API_KEY}"


def fetch_weather_data():
    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            st.error(f"Weather API failed with status code: {response.status_code}")
            return None, None, None

        data = response.json()

        if "main" not in data:
            st.error("Weather API response is missing 'main' key")
            return None, None, None

        # Get temperature in Fahrenheit from API
        temp_f = data["main"]["temp"]
        # Convert to Celsius
        temp_c = fahrenheitToCelsius(temp_f)
        humidity = data["main"]["humidity"]
        weather = data["weather"][0]["description"]

        return temp_c, humidity, weather

    except Exception as e:
        st.error(f"Error fetching weather data: {str(e)}")
        return None, None, None


# Fetch and display weather data
temp, humidity, weather = fetch_weather_data()

# Columns for metrics
col1, col2, col3, col4 = st.columns(4)


import textwrap

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


# Display metrics
with col1:
    if temp is not None:
        metric_box_style("Temperature ", f"{temp:.1f}°C", "#131b59", TEMP_ICON)
    else:
        metric_box_style("Temperature", "N/A", "#131b59")

with col2:
    if humidity is not None:
        metric_box_style("Humidity", f"{humidity}%", "#edaf10", HUMIDITY_ICON)
    else:
        metric_box_style("Humidity", "N/A", "#edaf10")

with col3:
    if weather is not None:
        metric_box_style("Weather🌤️", weather.capitalize(), "#57360b")
    else:
        metric_box_style("Weather🌤️", "N/A", "#57360b")

with col4:
    # Placeholder for soil moisture (replace with actual data)
    metric_box_style("Soil Moisture", "5.5%", "#2e6b3e", SOIL_MOISTURE_ICON)



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


USE_MOCK = True # we can set this API TO true when is ready

def get_upper_plants_data_func():
    """
    Returns
    current: dict of last readings
    target: target values
    history: DataFrame is index for charts by time
    """
    if USE_MOCK:
        #current reading will be read
        time_series = pd.date_range(datetime.now() - timedelta(hours=24), periods=10, freq="H")

        history = pd.DataFrame({
            "temp_c: ": 24 + np.cumsum(np.random.normal(0, 0.012, len(time_series))),
        }, index=time_series)

        current = {
            "temp_c": history["temp_c"].iloc[-1],
        }

        target = {"temp_c" : 25.0}
        return current, target,history


def metric_vs_target_alert_func(label, value, low, high, target, unit=""):
    """
    ## ideally make fixed metrics so that we can analyze under those metrics ranges
   green alert" [low range  > green alert for good <  high range  ]
    """


section_header_function("Upper Plants", HANGING_POT_ICON)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Temperature", "24.3°C", "+0.6°C")
with k2:
    st.metric("Humidity", "60%", "-2%")
with k3:
    st.metric("Light", "820 lx", "+40 lx")
with k4:
    st.metric("Soil Moisture", "5.5%", "-0.5% from target")


