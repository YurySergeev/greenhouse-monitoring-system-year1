from datetime import datetime

import streamlit as st


# --------------------------------------------------
# Page header
# --------------------------------------------------

def render_zone_header(zone_name: str):
    st.markdown(f"""
    <div class="page-header">
        <div>
            <p class="page-title">{zone_name}</p>
            <p class="page-subtitle">Real-time environmental monitoring</p>
        </div>
        <div class="live-badge">
            <div class="live-badge-dot"></div>
            Live
        </div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# Refresh bar
# --------------------------------------------------

def render_refresh_update():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    col_time, col_btn = st.columns([5, 1])
    with col_time:
        # Get theme color from session state, fallback to #ffffff
        color = st.session_state.get("zone_text_color", "#ffffff")
        st.markdown(f'<p style="font-size: 0.875rem; color: {color}; margin: 0;">Last synced: {now}</p>', unsafe_allow_html=True)
    with col_btn:
        if st.button("Refresh", use_container_width=True):
            st.session_state["last_update"] = datetime.now()
            st.cache_data.clear()
            st.rerun()


# --------------------------------------------------
# Zone 1 sub-section nav + controls
# --------------------------------------------------

def render_zone1_top_controls():
    if "zone1_section" not in st.session_state:
        st.session_state["zone1_section"] = "Upper Plants"
    if "temp_unit" not in st.session_state:
        st.session_state["temp_unit"] = "°C"

    col_controls, col_alerts = st.columns(2)

    with col_controls:
        with st.container(border=True):
            st.markdown("**Temperature unit**")
            unit = st.radio(
                "Temperature Unit",
                ["°C", "°F"],
                horizontal=True,
                label_visibility="collapsed",
                key="temp_unit",
            )

    with col_alerts:
        with st.container(border=True):
            st.markdown("**Alerts**")
            # Get theme color from session state, fallback to #ffffff
            color = st.session_state.get("zone_text_color", "#ffffff")
            st.markdown(f'<p style="font-size: 0.875rem; color: {color}; margin: 0;">No active alerts — all sensors nominal.</p>', unsafe_allow_html=True)

    section = st.session_state["zone1_section"]
    return section, unit


# --------------------------------------------------
# Individual metric card
# --------------------------------------------------

def render_metric_card(title: str, value: str, chip_class: str, icon: str,
                       trend: str = "", trend_class: str = ""):
    trend_html = f'<div class="metric-trend {trend_class}">{trend}</div>' if trend else ""
    html = f"""
    <div class="metric-card">
        <div class="metric-icon-chip {chip_class}">{icon}</div>
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        {trend_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# --------------------------------------------------
# Metrics row (4 cards)
# --------------------------------------------------

def render_metrics_row(temp, humidity, weather, temp_unit="°C"):
    if temp is not None:
        display_temp = (
            f"{float(temp):.1f}<span class='metric-unit'>°C</span>"
            if temp_unit == "°C"
            else f"{round(temp * 9/5 + 32, 1)}<span class='metric-unit'>°F</span>"
        )
    else:
        display_temp = "N/A"

    display_humidity = f"{humidity}<span class='metric-unit'>%</span>" if humidity is not None else "N/A"
    display_weather  = str(weather).title() if weather is not None else "N/A"

    col1, col2, col3 = st.columns(3)

    with col1:
        render_metric_card("Temperature", display_temp, "chip-green", "🌡️",
                           "↑ 0.3° from 1h ago", "trend-up")
    with col2:
        render_metric_card("Humidity", display_humidity, "chip-blue", "💧",
                           "— stable")
    with col3:
        render_metric_card("Weather",
                           f'<span style="font-size:18px;font-weight:500;">{display_weather}</span>',
                           "chip-gray", "🌤️", "Akron, OH")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# --------------------------------------------------
# Section header
# --------------------------------------------------

def render_section_header(title: str, icon = None):
    # Added a space after the closing span tag so it doesn't crowd the title if an icon exists
    icon_html = f'<span style="font-size:18px;">{icon}</span> ' if icon else ""
    
    # Placed {icon_html} and the <h2> tag on the same line
    html = f"""
    <div>
        <div class="section-title-container">
            {icon_html}<h2 class="section-title">{title}</h2>
        </div>
        <div class="section-divider"></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

