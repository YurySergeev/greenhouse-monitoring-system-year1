from operator import index

import streamlit as st
from pathlib import Path


st.set_page_config(page_title="Greenhouse Home", layout="wide", initial_sidebar_state="expanded")

#header
st.title("Kent State Greenhouse Monitoring System")
st.divider()
#introduction to the page
st.subheader("Welcome") #i need a wave emoji here

st.write(""" 
This system will help Kent State Greenhouse Monitoring System of zone
to visualize the conditions accross different zones.
""")

## anotheR subtitle
st.subheader("What We Are Monitoring")

column1, column2, column3 = st.columns(3)

##TODO:NEDDS STYLING
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
##TODO:NEDDS STYLING
with column2:
    st.markdown(
        """
        **System Capabilities**
        - Multi-zone greenhouse monitoring  
        - Data visualization through dashboards and analytics  
        - Alert detection for  conditions  
        - Communication with Raspberry Pi sensor systems  
        """
    )



#sidebar
st.sidebar.title("Zones")
zone_selection = st.sidebar.selectbox(
    "Select a zone",
    ["Select a zone", "Zone 1", "Zone 2"],
    index=0
)

#select zone
if zone_selection == "Zone 1":
    st.switch_page("pages/1_zone1.py")

#image
BASE_DIR = Path(__file__).parent #directory on the front end folder
IMG = BASE_DIR / "assets/greenhouse.jpg" #path

#green house image display
st.image(str(IMG), width="stretch")

#this is to hide the file name on gthe sidebar

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



