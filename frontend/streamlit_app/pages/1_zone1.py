import streamlit as st
from datetime import datetime
from streamlit import subheader

#every file namae.py gets on the side bar
#this helps for ui to look CLEANER
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
st.sidebar.caption("Zone 1 navigation") #sidebar caption

#sidebar for zone 1
zone1_selection = st.sidebar.selectbox(
    "Select a metric for zone 1",
    ["Dashboard", "Analytics", "Zone 1 Alerts"],
    index=0
)



#last updated as page  refresh
st.caption(
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

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

st.divider()

