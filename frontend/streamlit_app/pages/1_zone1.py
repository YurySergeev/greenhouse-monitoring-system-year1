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
import random # this will generate random numbers to use it as mmock for hecking status conditions on zone plnat

#--------------------------- charts libraries
import plotly.express as px
import plotly.graph_objects as go #gauge chart




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

UPPER_ZONE_RULES = {
    "temp" : {"low": 18.0, "high": 25.0},
    "humidity" : { "low": 45.0, "high": 75.0},
    "light" : {"low" : 600.0, "high": 1200.0},
    "soil" : {"low": 25.0, "high": 45.0 },
}

def metric_in_range(label, value, low, high, unit=""):
    #in range will show ok, green pill
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



#mock with import rand library for values, later will be replace with db sensor data
light = random.randint(600, 1200)
soil = random.uniform(10, 60)


section_header_function("Upper Plants", HANGING_POT_ICON)

k1, k2, k3, k4 = st.columns(4)
with k1:
    rule = UPPER_ZONE_RULES["temp"]
    metric_in_range("Temperature", temp, rule["low"], rule["high"], "C")
with k2:
    rule = UPPER_ZONE_RULES["humidity"]
    metric_in_range("Humidity", humidity, rule["low"], rule["high"], "%")
with k3:
    rule = UPPER_ZONE_RULES["light"]
    metric_in_range("Light", light, rule["low"], rule["high"], "lx")

with k4:
    rule = UPPER_ZONE_RULES["soil"]
    metric_in_range("Soil", soil, rule["low"], rule["high"], "%")


hours = pd.date_range(end=pd.Timestamp.now(), periods=24, freq="H")
temp_series = np.random.normal(22,2,24)

df = pd.DataFrame({
    "time": hours,
    "Temperature": temp_series,
    "Humidity": humidity,
})


c1, c2 = st.columns(2)




with c1:
    fig = px.line(df, x="time", y="Temperature", template="plotly_dark", title="Temperature (°C)")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.line(df, x="time", y="Humidity", template="plotly_dark", title="Humidity (%)")
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)

#gauge

value = soil
with c3:
    value = soil

    with c3:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={
                'text': "Soil (%)",
                'font': {'size': 22, 'color': '#2F4F4F'}
            },
            number={'font': {'size': 40, 'color': '#2F4F4F'}},
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickwidth': 1,
                    'tickcolor': '#A9A9A9'
                },
                'bar': {'color': '#4C78A8'},
                'bgcolor': 'white',
                'borderwidth': 1.5,
                'bordercolor': '#D3D3D3',
                'steps': [
                    {'range': [0, 50], 'color': '#E5E8E8'},
                    {'range': [50, 80], 'color': '#C8D6E5'},
                    {'range': [80, 100], 'color': '#A3C1AD'}
                ],
                'threshold': {
                    'line': {'color': '#FF6F61', 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',  # fully transparent
            plot_bgcolor='rgba(0,0,0,0)',  # transparent plot area
            font={'color': 'white'}  # match dark theme
        )

        st.plotly_chart(fig, use_container_width=True)
