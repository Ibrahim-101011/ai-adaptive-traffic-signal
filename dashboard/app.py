import streamlit as st
import pandas as pd
import time
import os

st.set_page_config(
    page_title="AI Adaptive Traffic Control Telemetry",
    page_icon="🚦",
    layout="wide"
)

CSV_PATH = "data/processed/traffic_telemetry.csv"

def load_telemetry():
    if not os.path.exists(CSV_PATH) or os.stat(CSV_PATH).st_size == 0:
        return None
    try:
        df = pd.read_csv(CSV_PATH)
        return df
    except Exception:
        return None

# Title & Status Header
st.title("🚦 AI-Adaptive Traffic Signal Telemetry Dashboard")
st.markdown("Real-time telemetry and density monitoring for Hardware-in-the-Loop (HIL) 4-Way Intersection.")

# Auto-refresh loop container
dashboard_placeholder = st.empty()

# Sidebar Controls
st.sidebar.header("Configuration & Refresh")
refresh_rate = st.sidebar.slider("Polling Interval (seconds)", min_value=0.5, max_value=3.0, value=1.0, step=0.5)
st.sidebar.markdown("---")
st.sidebar.markdown("**Intersection Legend**")
st.sidebar.markdown("- **Road 1:** North Approach")
st.sidebar.markdown("- **Road 2:** East Approach")
st.sidebar.markdown("- **Road 3:** South Approach")
st.sidebar.markdown("- **Road 4:** West Approach")

while True:
    df = load_telemetry()
    with dashboard_placeholder.container():
        if df is None or df.empty:
            st.warning("⚠️ Waiting for telemetry data... Make sure `python src/main.py` is actively running.")
        else:
            latest = df.iloc[-1]

            # Primary KPI Metrics
            col1, col2, col3, col4 = st.columns(4)

            mode_val = str(latest["mode"])
            mode_color = "red" if mode_val == "EMERGENCY" else "blue"
            col1.metric("Control Mode", mode_val)

            active_road_label = str(latest["active_road"]).upper()
            col2.metric("Active Approach", active_road_label)

            state_val = str(latest["state"])
            col3.metric("Signal Aspect", state_val)

            timer_val = f"{int(latest['remaining_seconds'])}s"
            col4.metric("Phase Countdown", timer_val)

            st.markdown("---")

            # 4-Way Road State Cards
            st.subheader("Current Approach Queue & Density")
            r_cols = st.columns(4)

            roads = ["road1", "road2", "road3", "road4"]
            for i, r in enumerate(roads):
                count = int(latest[f"{r.replace('road', 'r')}_count"])
                pcu = float(latest[f"{r.replace('road', 'r')}_pcu"])
                is_active = (r == str(latest["active_road"]))

                badge = "🔴 RED"
                if is_active:
                    badge = "🟢 GREEN" if state_val == "GREEN" else ("🟡 YELLOW" if state_val == "YELLOW" else "🔴 RED")

                with r_cols[i]:
                    st.markdown(f"### {r.upper()}")
                    st.write(f"**Aspect:** {badge}")
                    st.metric(label="Vehicles Queued", value=f"{count}")
                    st.metric(label="PCU Density", value=f"{pcu:.1f}")

            st.markdown("---")

            # Live Analytics Charts
            st.subheader("Live Queue Trends (Recent Cycles)")
            chart_data = df.tail(40)[["timestamp", "r1_count", "r2_count", "r3_count", "r4_count"]].set_index("timestamp")
            chart_data.columns = ["North (R1)", "East (R2)", "South (R3)", "West (R4)"]
            st.line_chart(chart_data)

            # Historical Telemetry Table
            with st.expander("Recent Raw Telemetry Records (Last 10 frames)"):
                st.dataframe(df.tail(10))

    time.sleep(refresh_rate)