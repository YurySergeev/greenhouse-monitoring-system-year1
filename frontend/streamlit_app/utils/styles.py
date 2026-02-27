import streamlit as st
from pathlib import Path

def load_css():
    css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    css = css_path.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)