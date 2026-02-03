import streamlit as st

st.set_page_config(page_title="Greenhouse Control", layout="wide")

st.sidebar.header("Greenhouse control")

#side bar list for each each zone option
zone = st.sidebar.selectbox(
    "Select greenhouse zone",
    ["Zone 1", "Zone 2"],
)

st.title("Greenhouse Control")
st.write("Select a zone from the sidebar")

#zone selection
if zone == "Zone 1":
    st.switch_page("pages/1_zone1.py")
elif zone == "Zone 2": #possible zone 2 selection
    st.warning("Zone 2 coming soon ")
