from pathlib import Path
import streamlit as st

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
LOGO_PATH  = ASSETS_DIR / "logo3.png"


def render_sidebar():
    with st.sidebar:
        # Logo
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=100)

        st.markdown("### Greenhouse")
        st.caption("Kent State University")
        st.divider()

        # Zone navigation
        st.markdown('<p class="section-label">Zones</p>', unsafe_allow_html=True)

        if st.button("Zone 1", use_container_width=True):
            st.switch_page("pages/1_zone1.py")

        st.button("Zone 2", use_container_width=True, disabled=True)

        st.divider()
        st.caption("System online · All sensors nominal")