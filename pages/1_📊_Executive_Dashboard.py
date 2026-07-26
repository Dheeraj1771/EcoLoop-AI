import plotly.graph_objects as go
import streamlit as st

from core_logic import inject_custom_css, load_and_calculate_kpis, render_kpi_row

st.set_page_config(page_title="Executive Dashboard", layout="wide")
inject_custom_css()

# --- Page-Specific CSS ---
st.markdown("""
    <style>
    .insight-card-purple { 
        background-color: var(--secondary-background-color); 
        padding: 25px; 
        border-radius: 10px; 
        border-top: 5px solid #9C27B0; 
        color: var(--text-color); 
        margin-bottom: 25px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
    }
    </style>
""", unsafe_allow_html=True)

b_df, a_df, kpis = load_and_calculate_kpis()

# --- HERO HEADER ---
st.markdown("<h2 style='text-align: center; color: #9C27B0;'>📊 Executive Dashboard</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>High-Level Financial & Telemetry Overview</h4>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Render the dynamic global KPIs
render_kpi_row(kpis)
st.markdown("<br>", unsafe_allow_html=True)

# Stunning Insight Card
st.markdown("""
<div class="insight-card-purple">
    <h4>⚡ Autonomous Actuation Analysis</h4>
    <p><b>Executive Summary:</b> This telemetry feed provides a transparent view into the AI's reasoning loop. It overlays the LLM's live temperature setpoint commands (Orange steps) against the facility's physical electrical response (Green line).</p>
    <p style="margin-bottom: 0;">Notice how the AI proactively adjusts the setpoints during occupied hours to undercut the rigid baseline schedule, resulting in direct reductions in kilowatt draw without violating the pre-programmed Honeywell safety constraints.</p>
</div>
""", unsafe_allow_html=True)

fig_main = go.Figure()
fig_main.add_trace(go.Scatter(x=b_df["time"], y=b_df["power_kW"], name="Baseline Power (kW)", line={"color": "rgba(200, 200, 200, 0.4)", "width": 1}))
fig_main.add_trace(go.Scatter(x=a_df["time"], y=a_df["power_kW"], name="EcoLoop Power (kW)", line={"color": "#4CAF50", "width": 2}))

if "ai_setpoint_C" in a_df.columns:
    fig_main.add_trace(go.Scatter(x=a_df["time"], y=a_df["ai_setpoint_C"], name="AI Setpoint (°C)", line={"color": "#FF9800", "width": 2, "shape": "hv"}, yaxis="y2"))

fig_main.update_layout(
    xaxis={"title": "July Timeline"},
    yaxis={"title": "Kilowatts (kW)", "side": "left"},
    yaxis2={"title": "Setpoint (°C)", "overlaying": "y", "side": "right", "range": [20, 30]},
    hovermode="x unified", legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    margin={"l": 0, "r": 0, "t": 30, "b": 0}
)
st.plotly_chart(fig_main, use_container_width=True)