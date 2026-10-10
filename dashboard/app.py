import os
import time
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# ---------------------------------------------------------
# Page Setup & Theme
# ---------------------------------------------------------
st.set_page_config(
    page_title="Traffic Operations Command Center",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Dark Command Center Aesthetics)
st.markdown("""
<style>
    /* Dark Theme Base */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Top Header */
    .dashboard-header {
        background: linear-gradient(90deg, #161b22, #0d1117);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px 24px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .dashboard-title {
        font-size: 24px;
        font-weight: 700;
        color: #f0f6fc;
        margin: 0;
    }
    .dashboard-subtitle {
        font-size: 13px;
        color: #8b949e;
        margin: 0;
    }

    /* Signal Approach Cards */
    .signal-card {
        background: #161b22;
        border-radius: 10px;
        border: 1px solid #30363d;
        padding: 16px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .signal-active-green {
        border: 2px solid #2ea043 !important;
        box-shadow: 0 0 15px rgba(46, 160, 67, 0.35);
    }
    .signal-active-yellow {
        border: 2px solid #d29922 !important;
        box-shadow: 0 0 15px rgba(210, 153, 34, 0.35);
    }
    .signal-active-red {
        border: 2px solid #f85149 !important;
        box-shadow: 0 0 15px rgba(248, 81, 73, 0.25);
    }
    .signal-bulb {
        height: 22px;
        width: 22px;
        border-radius: 50%;
        display: inline-block;
        margin: 0 4px;
    }
    .bulb-dim { background-color: #21262d; border: 1px solid #30363d; }
    .bulb-green { background-color: #2ea043; box-shadow: 0 0 10px #2ea043; }
    .bulb-yellow { background-color: #d29922; box-shadow: 0 0 10px #d29922; }
    .bulb-red { background-color: #f85149; box-shadow: 0 0 10px #f85149; }

    /* Metric Badges */
    .metric-badge {
        font-size: 28px;
        font-weight: 800;
        color: #58a6ff;
    }
    .metric-label {
        font-size: 12px;
        text-transform: uppercase;
        color: #8b949e;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

CSV_PATH = "data/processed/traffic_telemetry.csv"

# ---------------------------------------------------------
# Telemetry Loader with Concurrency Shield
# ---------------------------------------------------------
def load_data():
    if not os.path.exists(CSV_PATH):
        return None
    try:
        # Non-locking read
        df = pd.read_csv(CSV_PATH)
        if df.empty or len(df.columns) < 13:
            return None
        return df
    except Exception:
        return None

# ---------------------------------------------------------
# Sidebar Settings
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/traffic-light.png", width=64)
    st.markdown("### **System Controls**")
    refresh_rate = st.slider("Refresh Interval (seconds)", min_value=1.0, max_value=5.0, value=1.0, step=0.5)
    history_limit = st.select_slider("Telemetry Window (Points)", options=[30, 60, 120, 300], value=60)
    
    st.markdown("---")
    st.markdown("### **Road Geometries**")
    st.info("""
    - **Road 1**: North Approach
    - **Road 2**: East Approach
    - **Road 3**: South Approach
    - **Road 4**: West Approach
    """)

# ---------------------------------------------------------
# Data Processing
# ---------------------------------------------------------
df = load_data()

if df is None:
    st.warning("⏳ Waiting for telemetry feed... Make sure the simulation is running via `run_system.bat`.")
    time.sleep(1)
    st.rerun()

latest = df.iloc[-1]
active_road = str(latest["active_road"]).lower()
signal_state = str(latest["state"]).upper()
controller_mode = str(latest["mode"]).upper()
timer_sec = int(latest["remaining_seconds"])

# ---------------------------------------------------------
# Header Bar
# ---------------------------------------------------------
st.markdown(f"""
<div class="dashboard-header">
    <div>
        <h2 class="dashboard-title">🚦 Smart Traffic Control Hub</h2>
        <p class="dashboard-subtitle">Adaptive Real-Time Intersection Digital Twin • Real-Time Telemetry Feed</p>
    </div>
    <div style="text-align: right;">
        <span style="background: {'#238636' if controller_mode == 'ADAPTIVE' else '#1f6feb'}; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 13px;">
            {controller_mode} MODE
        </span>
        <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Last Ping: {latest['timestamp']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Executive KPI Row
# ---------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_vehicles = int(latest["r1_count"] + latest["r2_count"] + latest["r3_count"] + latest["r4_count"])
total_pcu = round(float(latest["r1_pcu"] + latest["r2_pcu"] + latest["r3_pcu"] + latest["r4_pcu"]), 1)

with kpi1:
    st.markdown(f"""
    <div class="signal-card">
        <div class="metric-label">Active Phase Approach</div>
        <div class="metric-badge" style="color: {'#3fb950' if signal_state == 'GREEN' else '#f85149'};">
            {active_road.upper()}
        </div>
        <div style="font-size: 12px; color: #8b949e;">Status: <b>{signal_state}</b></div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="signal-card">
        <div class="metric-label">Phase Countdown</div>
        <div class="metric-badge" style="color: #e3b341;">
            {timer_sec}s
        </div>
        <div style="font-size: 12px; color: #8b949e;">Dynamic Allotted Window</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="signal-card">
        <div class="metric-label">Intersection Density</div>
        <div class="metric-badge" style="color: #58a6ff;">
            {total_pcu} <span style="font-size: 16px;">PCU</span>
        </div>
        <div style="font-size: 12px; color: #8b949e;">Weighted Flow Load</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="signal-card">
        <div class="metric-label">Active Vehicle Queue</div>
        <div class="metric-badge" style="color: #bc8cff;">
            {total_vehicles} <span style="font-size: 16px;">Units</span>
        </div>
        <div style="font-size: 12px; color: #8b949e;">Across all 4 Approaches</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# Interactive 4-Way Approach Status Lights
# ---------------------------------------------------------
st.markdown("#### **Intersection Approach Status**")
road_cols = st.columns(4)

roads_info = [
    ("road1", "North Approach (R1)", latest["r1_count"], latest["r1_pcu"]),
    ("road2", "East Approach (R2)", latest["r2_count"], latest["r2_pcu"]),
    ("road3", "South Approach (R3)", latest["r3_count"], latest["r3_pcu"]),
    ("road4", "West Approach (R4)", latest["r4_count"], latest["r4_pcu"]),
]

for idx, (r_id, r_label, r_cnt, r_pcu) in enumerate(roads_info):
    is_active = (active_road == r_id)
    card_border_class = ""
    r_bulb, y_bulb, g_bulb = "bulb-dim", "bulb-dim", "bulb-dim"

    if is_active:
        if signal_state == "GREEN":
            card_border_class = "signal-active-green"
            g_bulb = "bulb-green"
        elif signal_state == "YELLOW":
            card_border_class = "signal-active-yellow"
            y_bulb = "bulb-yellow"
        else:
            card_border_class = "signal-active-red"
            r_bulb = "bulb-red"
    else:
        card_border_class = "signal-card"
        r_bulb = "bulb-red"

    with road_cols[idx]:
        st.markdown(f"""
        <div class="signal-card {card_border_class}">
            <div style="font-weight: 700; font-size: 14px; margin-bottom: 8px;">{r_label}</div>
            <div style="margin-bottom: 12px;">
                <span class="signal-bulb {r_bulb}"></span>
                <span class="signal-bulb {y_bulb}"></span>
                <span class="signal-bulb {g_bulb}"></span>
            </div>
            <div style="display: flex; justify-content: space-around; font-size: 13px; color: #8b949e;">
                <div>Queue: <b style="color: #f0f6fc;">{int(r_cnt)}</b></div>
                <div>PCU: <b style="color: #58a6ff;">{r_pcu:.1f}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# Telemetry Analytics Graphs (Plotly Dark)
# ---------------------------------------------------------
df_window = df.tail(history_limit)

chart_col1, chart_col2 = st.columns([2, 1])

with chart_col1:
    fig_timeline = go.Figure()
    colors = {"r1_pcu": "#388bfd", "r2_pcu": "#3fb950", "r3_pcu": "#e3b341", "r4_pcu": "#f85149"}
    labels = {"r1_pcu": "North (R1)", "r2_pcu": "East (R2)", "r3_pcu": "South (R3)", "r4_pcu": "West (R4)"}

    for col_name, color in colors.items():
        fig_timeline.add_trace(go.Scatter(
            x=list(range(len(df_window))),
            y=df_window[col_name],
            mode='lines',
            name=labels[col_name],
            line=dict(color=color, width=2.5),
            fill='tozeroy' if col_name == 'r1_pcu' else 'none',
            opacity=0.85
        ))

    fig_timeline.update_layout(
        title="<b>Real-Time PCU Congestion Curve</b>",
        title_font=dict(size=15, color="#f0f6fc"),
        plot_bgcolor="#161b22",
        paper_bgcolor="#161b22",
        font=dict(color="#8b949e", size=11),
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="#21262d", zeroline=False, title="Recent Samples"),
        yaxis=dict(showgrid=True, gridcolor="#21262d", zeroline=False, title="PCU Density")
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

with chart_col2:
    current_counts = [latest["r1_count"], latest["r2_count"], latest["r3_count"], latest["r4_count"]]
    labels_pie = ["North", "East", "South", "West"]
    pie_colors = ["#388bfd", "#3fb950", "#e3b341", "#f85149"]

    fig_donut = go.Figure(data=[go.Pie(
        labels=labels_pie,
        values=current_counts,
        hole=0.6,
        marker=dict(colors=pie_colors, line=dict(color='#0e1117', width=2)),
        textinfo='label+percent'
    )])

    fig_donut.update_layout(
        title="<b>Current Load Distribution</b>",
        title_font=dict(size=15, color="#f0f6fc"),
        plot_bgcolor="#161b22",
        paper_bgcolor="#161b22",
        font=dict(color="#8b949e", size=11),
        margin=dict(l=10, r=10, t=40, b=10),
        height=320,
        showlegend=False
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ---------------------------------------------------------
# Real-Time Event Audit Table
# ---------------------------------------------------------
with st.expander("📋 View Recent Telemetry Logs (Raw Stream)", expanded=False):
    st.dataframe(
        df_window.tail(15).sort_values("timestamp", ascending=False),
        use_container_width=True,
        hide_index=True
    )

# ---------------------------------------------------------
# Dynamic Refresh Loop
# ---------------------------------------------------------
time.sleep(refresh_rate)
st.rerun()