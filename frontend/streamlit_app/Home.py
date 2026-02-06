from operator import index
import streamlit as st
import requests
import time
from operator import index
from pathlib import Path

#bblue : 131b59
#yellow: edaf10
#brown: 57360b


st.set_page_config(page_title="Greenhouse Home", layout="wide", initial_sidebar_state="expanded")

# --------------- styling for divs ---------------------
st.markdown("""

<style>
.block-container { max-width: 1100px; padding-top: 2rem; }




/*title style*/
.ksuTitle {
padding: 26px, 26px, 20px 286px;
border-radius: 18px;
background: #edaf10;
box-shadow: 0, 10px 30px, rgba(0,0,0,0.35);
margin-bottom: 10px;
text-align: center;
}


.ksuTitle h1{
margin: 0; font-size: 40px; line-height: 1.05;
}

/*box description */
.box{
padding: 18;
border-radius: 16px;
background: #57360b;
border: 1px solid rgba(255,255,255,0.08);
text-align: center;
}

.box h3{
margin: 0 0 10px 0;
font-size: 25px;
}


.list{
 opacity: 0.75;
  font-size: 13px;
  margin-bottom: 10px;
}

.metrics{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  margin-top:10px;
  justify-content: center;
}

/*each small box*/
.metric{

padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  font-size: 12px;
  font-weight: 500;


}

hr { opacity: 0.15; }
</style>
""", unsafe_allow_html=True)

# --- side bar logo  ---
st.sidebar.image("assets/logo3.png", width=120)


# style for logo
st.sidebar.markdown(
    """
    <div style="
        text-align:center;
        font-size:13px;
        font-weight:600;
        opacity:0.85;
        margin-top:-26px;   
        margin-bottom:8px;
    ">
    
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.divider()




#title style
st.markdown("""
    <div class="ksuTitle">
    <h1> Kent State Green House Monitoring</h1>
   
    </div>
    """, unsafe_allow_html=True
)

#subtitle
st.markdown("<div class='system-description'> What the sensors monitor?</div> ", unsafe_allow_html=True)
left, right = st.columns(2, gap="large")

#left box
with left:
    st.markdown("""
    <div class="box">
      <h3>Environmental Metrics</h3>
      <div class="list">Per-zone sensor readings used to track growing conditions.</div>
      <div class="metrics">
        <div class="metric">Temperature</div>
        <div class="metric">Humidity</div>
        <div class="metric">Soil Moisture</div>
        <div class="metric">pH</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

#right box
with right:
    st.markdown("""
    <div class="box">
      <h3>System Capabilities</h3>
      <div class="list">Dashboards, analytics, and alerts to keep conditions stable.</div>
      <div class="metrics">
        <div class="metric">Zone dashboards & analytics</div>
        <div class="metric">Alerts</div>
        <div class="metric">Raspberry Pi integration</div>
      </div>
    </div>
    """, unsafe_allow_html=True)






#sidebar
st.sidebar.title("System Control")
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
IMG = BASE_DIR / "assets/greenhouse2.jpg" #path

st.markdown("<br>", unsafe_allow_html=True)

img_col = st.columns([1, 3, 1])[1]  # center column

with img_col:
    st.image(str(IMG), use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)


#keep this
#this is to hide the file.py name off the sidebar
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



