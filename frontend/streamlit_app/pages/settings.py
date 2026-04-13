import streamlit as st
from pathlib import Path
import matplotlib.colors as plt
from utils.themes import THEMES
from utils.sidebar import render_sidebar
from utils.styles import load_css
from utils.alerts import get_zone_alert, update_zone_alert, evaluate_temperature_alert, evaluate_humidity_alert
from utils.db import load_latest_reading, load_latest_sensor
from utils.weather import fetch_weather_data
from utils.emailer import is_email_configured


def c_to_f(temp_c: float) -> float:
	return (temp_c * 9.0 / 5.0) + 32.0


def f_to_c(temp_f: float) -> float:
	return (temp_f - 32.0) * 5.0 / 9.0

st.set_page_config(page_title="Settings", layout="wide")
load_css()

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

st.title("Settings")
st.write("Configure zone temperature and humidity alerts for plant-safe ranges.")

if "temp_unit" not in st.session_state:
	# Reuse the same key as zone pages so unit preference stays consistent.
	st.session_state["temp_unit"] = "°C"

unit = st.radio(
	"Temperature Unit",
	["°C", "°F"],
	horizontal=True,
	key="temp_unit",
)

zone_options = ["zone1", "zone2"]
zone_labels = {"zone1": "Zone 1", "zone2": "Zone 2"}

selected_zone = st.selectbox(
	"Zone",
	options=zone_options,
	format_func=lambda z: zone_labels.get(z, z.title()),
)

zone_settings = get_zone_alert(selected_zone)
# Seed the UI from persisted recipients, with legacy single-email fallback.
current_recipients = zone_settings.get("email_recipients") or []
if not current_recipients and zone_settings.get("email_to"):
	current_recipients = [zone_settings.get("email_to")]

min_c = float(zone_settings.get("temp_min_c", 18.0))
max_c = float(zone_settings.get("temp_max_c", 28.0))
humidity_min_pct = float(zone_settings.get("humidity_min_pct", 45.0))
humidity_max_pct = float(zone_settings.get("humidity_max_pct", 80.0))

if unit == "°F":
	# UI accepts Fahrenheit when selected, but settings are persisted in Celsius.
	default_min = round(c_to_f(min_c), 1)
	default_max = round(c_to_f(max_c), 1)
	input_min, input_max = 14.0, 140.0
else:
	default_min = round(min_c, 1)
	default_max = round(max_c, 1)
	input_min, input_max = -10.0, 60.0

# Build a live snapshot in the same priority order as Zone 1.
pico_latest = load_latest_sensor(zone=selected_zone, area="upper_plants")
mongo_latest = load_latest_reading(zone=selected_zone, area="upper_plants", source="openweather")
api_temp, api_humidity, _, _ = fetch_weather_data()

live_temp = api_temp
live_humidity = api_humidity

if mongo_latest:
	if mongo_latest.get("temp_c") is not None:
		live_temp = mongo_latest["temp_c"]
	if mongo_latest.get("humidity_pct") is not None:
		live_humidity = mongo_latest["humidity_pct"]

if pico_latest:
	if pico_latest.get("temperature_c") is not None:
		live_temp = pico_latest["temperature_c"]
	if pico_latest.get("humidity_rh") is not None:
		live_humidity = pico_latest["humidity_rh"]

# Reuse the same evaluation helpers used by runtime alerting on zone pages.
temp_alert_preview = evaluate_temperature_alert(live_temp, zone=selected_zone)
humidity_alert_preview = evaluate_humidity_alert(live_humidity, zone=selected_zone)

temp_min_display = c_to_f(min_c) if unit == "°F" else min_c
temp_max_display = c_to_f(max_c) if unit == "°F" else max_c
temp_value_display = c_to_f(live_temp) if (unit == "°F" and live_temp is not None) else live_temp

if live_temp is None:
	temp_status_line = "Temperature: no live data"
elif temp_alert_preview and temp_alert_preview["kind"] == "low":
	temp_status_line = f"Temperature: OUT OF RANGE (LOW) | {temp_value_display:.1f} {unit}"
elif temp_alert_preview and temp_alert_preview["kind"] == "high":
	temp_status_line = f"Temperature: OUT OF RANGE (HIGH) | {temp_value_display:.1f} {unit}"
else:
	temp_status_line = f"Temperature: IN RANGE | {temp_value_display:.1f} {unit}"

if live_humidity is None:
	humidity_status_line = "Humidity: no live data"
elif humidity_alert_preview and humidity_alert_preview["kind"] == "low":
	humidity_status_line = f"Humidity: OUT OF RANGE (LOW) | {float(live_humidity):.0f}%"
elif humidity_alert_preview and humidity_alert_preview["kind"] == "high":
	humidity_status_line = f"Humidity: OUT OF RANGE (HIGH) | {float(live_humidity):.0f}%"
else:
	humidity_status_line = f"Humidity: IN RANGE | {float(live_humidity):.0f}%"

st.markdown("### Alert Status")
# Compact preview card shows live status against configured limits.
with st.container(border=True):
	st.caption(f"{temp_status_line} (configured range: {temp_min_display:.1f} to {temp_max_display:.1f} {unit})")
	st.caption(
		f"{humidity_status_line} (configured range: {humidity_min_pct:.0f}% to {humidity_max_pct:.0f}%)"
	)

with st.form("temperature_alert_form"):
	st.markdown("### Temperature Alert Thresholds")
	alerts_enabled = st.toggle(
		"Enable temperature alerts",
		value=bool(zone_settings.get("enabled", True)),
	)

	col_min, col_max = st.columns(2)
	with col_min:
		temp_min_input = st.number_input(
			f"Minimum temperature ({unit})",
			min_value=input_min,
			max_value=input_max,
			value=default_min,
			step=0.5,
		)
	with col_max:
		temp_max_input = st.number_input(
			f"Maximum temperature ({unit})",
			min_value=input_min,
			max_value=input_max,
			value=default_max,
			step=0.5,
		)

	st.markdown("### Humidity Alert Thresholds")
	h_col_min, h_col_max = st.columns(2)
	with h_col_min:
		humidity_min_input = st.number_input(
			"Minimum humidity (%)",
			min_value=0.0,
			max_value=100.0,
			value=round(humidity_min_pct, 1),
			step=1.0,
		)
	with h_col_max:
		humidity_max_input = st.number_input(
			"Maximum humidity (%)",
			min_value=0.0,
			max_value=100.0,
			value=round(humidity_max_pct, 1),
			step=1.0,
		)

	st.markdown("### Email Notifications")
	email_enabled = st.toggle(
		"Send email when alert triggers",
		value=bool(zone_settings.get("email_enabled", False)),
	)
	email_add_input = st.text_input(
		"Add recipient email(s)",
		value="",
		placeholder="name@example.com or comma-separated list",
	)
	# Multi-select removal lets users prune existing recipients in one save.
	emails_to_remove = st.multiselect(
		"Remove recipient email(s)",
		options=current_recipients,
		default=[],
	)
	email_cooldown_minutes = st.number_input(
		"Cooldown between repeated emails (minutes)",
		min_value=1,
		max_value=720,
		value=int(zone_settings.get("email_cooldown_minutes", 30)),
		step=1,
	)

	save = st.form_submit_button("Save alert settings", use_container_width=True)

if save:
	try:
		# Convert user input to Celsius before storing and evaluating alerts.
		temp_min_c = f_to_c(temp_min_input) if unit == "°F" else temp_min_input
		temp_max_c = f_to_c(temp_max_input) if unit == "°F" else temp_max_input
		# Humidity values are stored as percentages and do not require conversion.
		# Apply removals first, then append newly entered recipients.
		new_recipients = [e for e in current_recipients if e not in emails_to_remove]
		if email_add_input.strip():
			add_parts = [part.strip() for part in email_add_input.replace(";", ",").replace("\n", ",").split(",")]
			for address in add_parts:
				if address and address.lower() not in {x.lower() for x in new_recipients}:
					new_recipients.append(address)

		update_zone_alert(
			zone=selected_zone,
			enabled=alerts_enabled,
			temp_min_c=temp_min_c,
			temp_max_c=temp_max_c,
			humidity_min_pct=humidity_min_input,
			humidity_max_pct=humidity_max_input,
			email_enabled=email_enabled,
			email_recipients=new_recipients,
			email_cooldown_minutes=int(email_cooldown_minutes),
		)
		st.success(f"Saved alert settings for {zone_labels.get(selected_zone, selected_zone)}.")
	except ValueError as exc:
		st.error(str(exc))

active_settings = get_zone_alert(selected_zone)
active_min_c = float(active_settings["temp_min_c"])
active_max_c = float(active_settings["temp_max_c"])

if unit == "°F":
	active_min = c_to_f(active_min_c)
	active_max = c_to_f(active_max_c)
else:
	active_min = active_min_c
	active_max = active_max_c

st.info(
	f"Current range for {zone_labels.get(selected_zone, selected_zone)}: "
	f"{active_min:.1f} {unit} to {active_max:.1f} {unit}"
	+ (" (alerts enabled)" if active_settings.get("enabled", True) else " (alerts disabled)")
)
st.info(
	f"Current humidity range for {zone_labels.get(selected_zone, selected_zone)}: "
	f"{float(active_settings.get('humidity_min_pct', 45.0)):.0f}% to "
	f"{float(active_settings.get('humidity_max_pct', 80.0)):.0f}%"
)

if active_settings.get("email_enabled", False):
	active_recipients = active_settings.get("email_recipients") or []
	if not active_recipients and active_settings.get("email_to"):
		active_recipients = [active_settings.get("email_to")]
	recipients_label = ", ".join(active_recipients) if active_recipients else "not set"
	st.caption(
		f"Email alerts: ON · recipients {recipients_label} · "
		f"cooldown {int(active_settings.get('email_cooldown_minutes', 30))} min"
	)
else:
	st.caption("Email alerts: OFF")

if not is_email_configured():
	st.warning(
		"SMTP is not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, and SMTP_FROM "
		"in your environment to enable email delivery."
	)
