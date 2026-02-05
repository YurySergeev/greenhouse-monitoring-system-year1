import streamlit as st
from datetime import datetime

# Every file name.py gets on the sidebar
# This helps for UI to look cleaner
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
st.title("Zone 1 – General Metrics")
st.sidebar.caption("Zone 1 navigation")

# Sidebar for zone 1
zone1_selection = st.sidebar.selectbox(
    "Select a metric for Zone 1",
    ["Dashboard", "Analytics", "Zone 1 Alerts"],
    index=0
)

# Last updated timestamp
st.caption(
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# Columns with data display
col1, col2, col3, col4 = st.columns(4)

# HTML function for each metric box
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

# Metric boxes (placeholder values for now)
with col1:
    metric_box_style("Temperature", "33.3 °C", "#FF9F43")

with col2:
    metric_box_style("Humidity", "46 %", "#2E86DE")

with col3:
    metric_box_style("pH Level", "5.5", "#8E44AD")

with col4:
    metric_box_style("Soil Moisture", "35 %", "#27AE60")

st.divider()
