import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core_logic import inject_custom_css, load_and_calculate_kpis

st.set_page_config(page_title="Deep Dive Analytics", layout="wide")
inject_custom_css()

# --- Page-Specific CSS for Insight Cards ---
st.markdown("""
    <style>
    .insight-card-blue { background-color: #1E1E1E; padding: 25px; border-radius: 10px; border-top: 5px solid #00BCD4; color: #FFFFFF; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .insight-card-green { background-color: #1E1E1E; padding: 25px; border-radius: 10px; border-top: 5px solid #4CAF50; color: #FFFFFF; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    /* Light Mode Overrides */
    @media (prefers-color-scheme: light) {
        .insight-card-blue { background-color: #f0f2f6; color: #000000; }
        .insight-card-green { background-color: #f0f2f6; color: #000000; }
    }
    </style>
""", unsafe_allow_html=True)

b_df, a_df, kpis = load_and_calculate_kpis()

# --- HERO HEADER ---
st.markdown("<h2 style='text-align: center; color: #00BCD4;'>📈 Deep Dive Analytics</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Advanced Telemetry & Thermodynamic Validation</h4>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🌡️ Thermal Comfort Heatmap", "📈 Cumulative Energy Savings"])
    
with tab1:
    # Stunning Insight Card for Heatmap
    st.markdown("""
    <div class="insight-card-blue">
        <h4>🌡️ Thermal Comfort Boundary Mapping (Fanger PMV)</h4>
        <p><b>Engineering Validation:</b> Energy savings are meaningless if human comfort is compromised. This heatmap actively tracks the <b>PMV (Predicted Mean Vote)</b> index across every hour of the simulation.</p>
        <ul style="margin-bottom: 0;">
            <li><b>Neutral Zones (-0.5 to +0.5):</b> Perfect thermal comfort maintained during standard operations.</li>
            <li><b>Optimization Zones (+0.5 to +1.0):</b> During peak afternoon heat, the LLM allows temperatures to drift slightly. Occupants feel mildly warm, but the facility drops massive electrical load—proving the AI aggressively negotiates the edge of comfort to maximize OpEx savings.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    heat_df = a_df.copy()
    heat_df["date"] = pd.to_datetime("2026-07-01") + pd.to_timedelta(heat_df["day"] - 182, unit="D")
    heatmap_pivot = heat_df.pivot(index="day", columns="hour", values="pmv")
    
    fig_heat = px.imshow(
        heatmap_pivot, labels={"x": "Hour of Day", "y": "Day of Year", "color": "PMV Level"},
        x=heatmap_pivot.columns, y=heatmap_pivot.index, color_continuous_scale="RdBu_r", zmin=-1.0, zmax=1.0, aspect="auto"
    )
    fig_heat.update_layout(height=550, hovermode="closest", margin={"l": 0, "r": 0, "t": 30, "b": 0})
    st.plotly_chart(fig_heat, use_container_width=True)

with tab2:
    # Stunning Insight Card for Cumulative Chart
    st.markdown("""
    <div class="insight-card-green">
        <h4>⚡ Compounding Efficiency (Cumulative kWh)</h4>
        <p><b>Engineering Validation:</b> This chart tracks the aggregate Kilowatt-hours (kWh) consumed over the facility's operational lifecycle. While hourly savings might look small in isolation, this visualizes the compounding financial value of the AI.</p>
        <p style="margin-bottom: 0;">The expanding <b>green shaded region</b> between the baseline schedule (grey dotted line) and the EcoLoop controller (solid green line) represents the physical volume of electricity, and therefore capital and carbon-saved through the LLM's micro-adjustments.</p>
    </div>
    """, unsafe_allow_html=True)
    
    b_cumulative = b_df["energy_kwh"].cumsum()
    a_cumulative = a_df["energy_kwh"].cumsum()
    
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(x=b_df["time"], y=b_cumulative, name="Baseline (kWh)", line={"color": "gray", "dash": "dot", "width": 2}))
    fig_cum.add_trace(go.Scatter(x=a_df["time"], y=a_cumulative, name="EcoLoop (kWh)", line={"color": "#4CAF50", "width": 3}, fill="tonexty", fillcolor="rgba(76, 175, 80, 0.2)"))
    fig_cum.update_layout(yaxis_title="Total Kilowatt-hours (kWh)", hovermode="x unified", margin={"l": 0, "r": 0, "t": 30, "b": 0})
    st.plotly_chart(fig_cum, use_container_width=True)