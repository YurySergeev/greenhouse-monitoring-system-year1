import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Greenhouse Home",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("Kent State Greenhouse Monitoring System")
st.divider()

# Introduction
st.subheader("Welcome 👋")
st.write(""" 
This system will help Kent State Greenhouse Monitoring System of zone
to visualize the conditions accross different zones.
""")

st.subheader("What We Are Monitoring")

column1, column2, column3 = st.columns(3)

with column1:
    st.markdown(
        """
        **Environmental Metrics**
        - Temperature  
        - Humidity  
        - pH Levels  
        - Soil Moisture  
        """
    )

with column2:
    st.markdown(
        """
        **System Capabilities**
        - Multi-zone greenhouse monitoring  
        - Data visualization through dashboards and analytics  
        - Alert detection for conditions  
        - Communication with Raspberry Pi sensor systems  
        """
    )

# Sidebar
st.sidebar.title("Zones")
zone_selection = st.sidebar.selectbox(
    "Select a zone",
    ["Select a zone", "Zone 1", "Zone 2"],
    index=0
)

# Select zone routing
if zone_selection == "Zone 1":
    st.switch_page("pages/1_zone1.py")

# Image
BASE_DIR = Path(__file__).parent
IMG = BASE_DIR / "assets/greenhouse.jpg"
st.image(str(IMG), use_container_width=True)

# Hide the zone1 page name on the sidebar (fragile if page order changes)
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] ul li:nth-child(2) {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)
