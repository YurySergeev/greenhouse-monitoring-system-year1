import streamlit as st
from pathlib import Path
import matplotlib.colors as plt
from utils.themes import THEMES
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Settings", layout="wide")

# ── Load CSS ───────────────────────────────────────────────────────────────────
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ── Initialize theme if not set ────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "Feeling Green"

# ── Apply current theme ────────────────────────────────────────────────────────
if True:
    current_theme = THEMES[st.session_state.theme]
    background_color = plt.XKCD_COLORS[current_theme["background"]]
    sidebar_color = plt.XKCD_COLORS[current_theme["sidebar"]]
    title_color = plt.XKCD_COLORS[current_theme["title"]]
    boxes_color = plt.XKCD_COLORS[current_theme["boxes"]]
    top_bar_color = plt.XKCD_COLORS[current_theme["top_bar"]]
    text_color = current_theme["text_color"]
    title_text_color = current_theme.get("title_text_color", text_color)
    caption_color = current_theme.get("caption_color", text_color)
    zone_text_color = current_theme.get("zone_text_color", text_color)

    # helper to resolve color
    def _resolve_color(value):
        if isinstance(value, str) and value.startswith("xkcd:"):
            return plt.XKCD_COLORS[value]
        return value

    subtitle_color = _resolve_color(current_theme.get("subtitle", current_theme["text_color"]))

    # Set theme variables
    st.markdown(f"""
    <style>
    :root {{
        --background-color: {background_color};
        --sidebar-color: {sidebar_color};
        --title-color: {title_color};
        --boxes-color: {boxes_color};
        --top-bar-color: {top_bar_color};
        --text-color: {text_color};
        --subtitle-color: {subtitle_color};
        --secondary-background-color: {boxes_color};
        --title-text-color: {title_text_color};
        --caption-color: {caption_color};
        --zone-text-color: {zone_text_color};
    }}
    
    /* Settings page text color overrides */
    * {{
        color: {title_text_color} !important;
    }}
    
    [data-testid="stMarkdown"] {{
        color: {title_text_color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

render_sidebar()

st.markdown("""
<div style="color: var(--title-text-color);">
    <h1 style="color: var(--title-text-color);">Settings</h1>
    <p style="color: var(--title-text-color);">This is the settings page.</p>
</div>
""", unsafe_allow_html=True)