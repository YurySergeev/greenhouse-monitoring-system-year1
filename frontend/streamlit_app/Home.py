import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Greenhouse — Kent State", layout="wide", page_icon="🌱")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH  = ASSETS_DIR / "logo3.png"
IMG_PATH   = ASSETS_DIR / "greenhouse2.jpg"

# ── Load CSS ───────────────────────────────────────────────────────────────────
css_path = BASE_DIR / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=100)
    st.markdown("### Greenhouse")
    st.caption("Kent State University")
    st.divider()

    st.markdown('<p class="section-label">Zones</p>', unsafe_allow_html=True)
    zone_selection = st.selectbox(
        "Navigate to zone",
        ["— select —", "Zone 1", "Zone 2"],
        label_visibility="collapsed",
    )
    if zone_selection == "Zone 1":
        st.switch_page("pages/1_zone1.py")

    st.divider()
    st.caption("System online · All sensors nominal")

# ── Page title ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:32px;">
    <p style="font-size:24px;font-weight:600;color:var(--text-color);margin:0;">
        Kent State Greenhouse
    </p>
    <p style="font-size:14px;color:var(--text-color);opacity:0.55;margin:4px 0 0 0;">
        Environmental monitoring system
    </p>
</div>
""", unsafe_allow_html=True)

# ── Info cards ─────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

# Shared card style — uses CSS variables so it works in light & dark
CARD = (
    "background:var(--secondary-background-color);"
    "border:1px solid rgba(128,128,128,0.2);"
    "border-radius:12px;"
    "padding:20px 22px;"
)

TEXT_PRIMARY   = "color:var(--text-color);"
TEXT_SECONDARY = "color:var(--text-color);opacity:0.55;"

with col1:
    st.markdown(f"""
    <div style="{CARD}">
        <div style="font-size:22px;margin-bottom:10px;">🌡️</div>
        <p style="font-size:13px;font-weight:600;{TEXT_PRIMARY}margin:0 0 10px 0;">Environmental sensors</p>
        <p style="font-size:12px;{TEXT_SECONDARY}margin:0 0 4px 0;">Temperature</p>
        <p style="font-size:12px;{TEXT_SECONDARY}margin:0 0 4px 0;">Humidity</p>
        <p style="font-size:12px;{TEXT_SECONDARY}margin:0 0 4px 0;">Soil moisture</p>
        <p style="font-size:12px;{TEXT_SECONDARY}margin:0;">pH</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="{CARD}">
        <div style="font-size:22px;margin-bottom:10px;">📡</div>
        <p style="font-size:13px;font-weight:600;{TEXT_PRIMARY}margin:0 0 10px 0;">System capabilities</p>
        <p style="font-size:12px;{TEXT_SECONDARY}margin:0 0 4px 0;">Zone dashboards</p>
        <p style="font-size:12px;{TEXT_SECONDARY}margin:0 0 4px 0;">Live alerts</p>
        <p style="font-size:12px;{TEXT_SECONDARY}margin:0 0 4px 0;">Historical charts</p>
        <p style="font-size:12px;{TEXT_SECONDARY}margin:0;">Raspberry Pi integration</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="{CARD}">
        <div style="font-size:22px;margin-bottom:10px;">🗂️</div>
        <p style="font-size:13px;font-weight:600;{TEXT_PRIMARY}margin:0 0 10px 0;">Active zones</p>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <div style="width:8px;height:8px;border-radius:50%;background:#10B981;flex-shrink:0;"></div>
            <span style="font-size:12px;{TEXT_PRIMARY}">Zone 1 — online</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:8px;height:8px;border-radius:50%;background:rgba(128,128,128,0.4);flex-shrink:0;"></div>
            <span style="font-size:12px;{TEXT_SECONDARY}">Zone 2 — coming soon</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Greenhouse image ───────────────────────────────────────────────────────────
st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

if IMG_PATH.exists():
    st.image(str(IMG_PATH), use_container_width=True,
             caption="Kent State University greenhouse facility")