import streamlit as st
from datetime import datetime

from streamlit import subheader




#browser tab title
st.set_page_config(page_title="Zone 1 Dashboard", layout="wide")

st.sidebar.header("Greenhouse control") #sidebar

#this navigate between pages, dropdown
zone = st.sidebar.selectbox(
    "Select greenhouse zone",
    ["Zone 1", "Zone 2"],
    index=0
)

#“This page is only valid for Zone 1
#If the user selects anything else,
# send them back to the main page and stop rendering.
#until we work on a new page
if zone != "Zone 1":
    st.switch_page("main.py")
    st.stop()


#main content
st.title("Zone 1 Dashboard")
st.caption("UI mock")

#columns with its data display
col1, col2, col3, col4 = st.columns(4)

#html/python function return params to use for each column
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


#column1 returning values from the function
with col1:
    metric_box_style( "Temperature", "33.3C", "#FF9F43")

#column 2 returning
with col2:
    metric_box_style( "Humidity", "46%.", "#2E86DE")

#column 3 returning values
with col3:
    metric_box_style( "pH levels", "5.5%.", "#8E44AD")

#box 4 returning values
with col4:
    metric_box_style( "Soil Moisture", "5.5%.", "#27AE60")


st.divider()

#last updated as page  refresh
st.caption(
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)