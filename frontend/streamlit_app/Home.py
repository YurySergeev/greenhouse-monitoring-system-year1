import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Greenhouse Home", layout="wide")

# Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

LOGO_PATH = ASSETS_DIR / "logo3.png"
IMG_GREENHOUSE = ASSETS_DIR / "greenhouse2.jpg"

# Sidebar
st.sidebar.image(str(LOGO_PATH), width=120)
st.sidebar.title("System Control")

zone_selection = st.sidebar.selectbox(
    "Select a zone",
    ["Select a zone", "Zone 1", "Zone 2"],
)

if zone_selection == "Zone 1":
    st.switch_page("pages/1_zone1.py")

# Title
st.title("Kent State Greenhouse Monitoring")

st.subheader("What the sensors monitor")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Environmental Metrics")
    st.write("• Temperature")
    st.write("• Humidity")
    st.write("• Soil Moisture")
    st.write("• pH")

with col2:
    st.markdown("### System Capabilities")
    st.write("• Zone dashboards")
    st.write("• Alerts")
    st.write("• Raspberry Pi integration")

# Image
if IMG_GREENHOUSE.exists():
    st.image(str(IMG_GREENHOUSE), use_container_width=True)