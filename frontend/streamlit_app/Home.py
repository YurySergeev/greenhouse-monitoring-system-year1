from operator import index
import streamlit as st
import requests
import time
from operator import index
from pathlib import Path
import matplotlib.colors as plt

from utils.styles import load_css
load_css()

# bblue : 131b59
# yellow: edaf10
# brown: 57360b
# colors: 
# really like: coffee & greenish grey (earth day vibes), dark sage & greenish grey
# potentially implement themes: go flashes!, earth day vibes, feeling green, etc

# Define themes
THEMES = {
    "Earth Day Vibes": {
        "background": "xkcd:greenish grey",
        "sidebar": "xkcd:coffee",
        "title": "xkcd:coffee",
        "boxes": "xkcd:coffee",
        "top_bar": "xkcd:coffee",
        "text_color": "#ffffff"
    ,
        # optional override for specific subtitle color (defaults to text_color)
        "subtitle": "#ffffff"
    },
    "Feeling Green": {
        "background": "xkcd:greenish grey",
        "sidebar": "xkcd:dark sage",
        "title": "xkcd:dark sage",
        "boxes": "xkcd:dark sage",
        "top_bar": "xkcd:dark sage",
        "text_color": "#ffffff",
        "subtitle": "#ffffff"
    },
    "Go Flashes!": {
        "background": "xkcd:silver",
        "sidebar": "xkcd:blue",
        "title": "xkcd:blue",
        "boxes": "xkcd:blue",
        "top_bar": "xkcd:blue",
        "text_color": "#ffd700",
        "subtitle": "xkcd:blue"  
    }
}

# Initialize session state for theme
if "theme" not in st.session_state:
    st.session_state.theme = "Earth Day Vibes"

# Get current theme colors
current_theme = THEMES[st.session_state.theme]
background_color = plt.XKCD_COLORS[current_theme["background"]]
sidebar_color = plt.XKCD_COLORS[current_theme["sidebar"]]
title_color = plt.XKCD_COLORS[current_theme["title"]]
boxes_color = plt.XKCD_COLORS[current_theme["boxes"]]
top_bar_color = plt.XKCD_COLORS[current_theme["top_bar"]]
text_color = current_theme["text_color"]

# helper to resolve either raw hex or xkcd color name

def _resolve_color(value):
    if isinstance(value, str) and value.startswith("xkcd:"):
        return plt.XKCD_COLORS[value]
    return value

# subtitle color can be overridden per theme, fallback to text_color
subtitle_color = _resolve_color(current_theme.get("subtitle", current_theme["text_color"]))

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

LOGO_PATH = ASSETS_DIR / "logo3.png"
IMG_GREENHOUSE = ASSETS_DIR / "greenhouse2.jpg"



st.set_page_config(page_title="Greenhouse Home", layout="wide", initial_sidebar_state="expanded")

# --------------- styling for divs ---------------------
st.markdown(f"""

<style>
.block-container {{ max-width: 1100px; padding-top: 2rem; }}

/*sets background color*/
.stApp {{
    background-color: {background_color};
}}


/*title style*/
.ksuTitle {{
padding: 26px, 26px, 20px 286px;
border-radius: 18px;
background: {title_color};
box-shadow: 0, 10px 30px, rgba(0,0,0,0.35);
margin-bottom: 10px;
text-align: center;
}}


.ksuTitle h1{{
margin: 0; font-size: 40px; line-height: 1.05; color: {text_color};
}}

/*box description */
.box{{
padding: 18;
border-radius: 16px;
background: {boxes_color};
border: 1px solid rgba(255,255,255,0.08);
text-align: center;
}}

.box h3{{
margin: 0 0 10px 0;
font-size: 25px;
}}


.list{{
 opacity: 0.75;
  font-size: 13px;
  margin-bottom: 10px;
}}

.metrics{{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  margin-top:10px;
  justify-content: center;
}}

/*each small box*/
.metric{{

padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  font-size: 12px;
  font-weight: 500;


}}

hr {{ opacity: 0.15; }}

/* Top bar */
[data-testid="stHeader"] {{
    background-color: {top_bar_color};
}}
</style>
""", unsafe_allow_html=True)

# --- side bar logo  ---
st.sidebar.image(str(LOGO_PATH), width=120)

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

# title style
st.markdown("""
    <div class="ksuTitle">
    <h1> Kent State Green House Monitoring</h1>

    </div>
      """, unsafe_allow_html=True
            )

# subtitle
st.markdown(f"""
<div style="text-align: center; font-size: 28px; margin: 20px 0; color: {subtitle_color};">
    <span style="letter-spacing: 15px;"> • • </span>&nbsp;What the sensors monitor?&nbsp;<span style="letter-spacing: 15px;"> • • </span>
</div>
""", unsafe_allow_html=True)
left, right = st.columns(2, gap="large")

# left box
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

# right box
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

# sidebar
st.sidebar.title("System Control")
zone_selection = st.sidebar.selectbox(
    "Select a zone",
    ["Select a zone", "Zone 1", "Zone 2"],
    index=0
)

# select zone
if zone_selection == "Zone 1":
    st.switch_page("pages/1_zone1.py")

# Theme selector in sidebar (bottom left)
st.sidebar.divider()
if st.sidebar.button("🌿 Change Theme", key="theme_button", help="Cycle through themes", use_container_width=True):
    # Cycle through themes
    themes_list = list(THEMES.keys())
    current_index = themes_list.index(st.session_state.theme)
    next_index = (current_index + 1) % len(themes_list)
    st.session_state.theme = themes_list[next_index]
    st.rerun()

# Greenhouse image centered
img_col = st.columns([1, 3, 1])[1]

with img_col:
    st.markdown('<div style="margin-top: 80px;">', unsafe_allow_html=True)
    if IMG_GREENHOUSE.exists():
        st.image(str(IMG_GREENHOUSE), use_container_width=True)
    else:
        st.info("Greenhouse image not found at: " + str(IMG_GREENHOUSE))
    st.markdown('</div>', unsafe_allow_html=True)

# Page break with leaf and dots
st.markdown("""
<div style="text-align: center; margin: 40px 0; font-size: 24px; letter-spacing: 15px;">
    • • • • • • 🌱 • • • • • •
</div>
""", unsafe_allow_html=True)

# keep this
# this is to hide the file.py name off the sidebar
st.markdown(f"""
    <style>
    /* Hide only the second page (zone1) */
    [data-testid="stSidebarNav"] ul li:nth-child(2) {{
        display: none;
    }}
    /* Change sidebar background color */
    .stSidebar {{
        background-color: {sidebar_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)