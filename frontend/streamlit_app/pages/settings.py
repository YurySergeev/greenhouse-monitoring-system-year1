import streamlit as st
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Settings", layout="wide")

render_sidebar()

st.title("Settings")
st.write("This is the settings page.")