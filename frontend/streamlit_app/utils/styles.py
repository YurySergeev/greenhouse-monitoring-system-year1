import streamlit as st
from pathlib import Path


def load_css():
    # Works whether utils/ is one or two levels below the project root
    here = Path(__file__).resolve().parent  # utils/

    candidates = [
        here.parent / "assets" / "style.css",   # streamlit_app/assets/style.css
        here.parent / "style.css",               # streamlit_app/style.css
        here.parent.parent / "assets" / "style.css",
    ]

    for css_path in candidates:
        if css_path.exists():
            st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)
            return

    st.warning("style.css not found — checked: " + ", ".join(str(p) for p in candidates))