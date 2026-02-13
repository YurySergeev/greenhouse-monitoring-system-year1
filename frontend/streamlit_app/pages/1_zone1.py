from urllib import response
import streamlit as st
from datetime import datetime
import os
from streamlit import subheader
import requests
import time
from utils.conversion import fahrenheitToCelsius
from dotenv import load_dotenv
from pathlib import Path
import os

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


def metric_box_style(title, value, color):
    st.markdown(
        f"""
        <div style="
            background-color: {color};
            padding: 18px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.12);
        ">
            <div style="font-size: 22px; font-weight: 700; margin-bottom: 10px;">
                {title}
            </div>
            <div style="font-size: 32px; font-weight: 800;">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Display metrics
with col1:
    if temp is not None:
        metric_box_style("Temperature", f"{temp:.1f}°C", "#131b59")
    else:
        metric_box_style("Temperature", "N/A", "#131b59")

with col2:
    if humidity is not None:
        metric_box_style("Humidity", f"{humidity}%", "#edaf10")
    else:
        metric_box_style("Humidity", "N/A", "#edaf10")

with col3:
    if weather is not None:
        metric_box_style("Weather", weather.capitalize(), "#57360b")  # <-- Missing ) was here
    else:
        metric_box_style("Weather", "N/A", "#57360b")

with col4:
    # Placeholder for soil moisture (replace with actual data)
    metric_box_style("Soil Moisture", "5.5%", "#2e6b3e")