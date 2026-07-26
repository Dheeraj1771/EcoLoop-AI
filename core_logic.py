import pandas as pd
import streamlit as st

COMMERCIAL_RATE_INR = 8.0 
GRID_EMISSION_FACTOR = 0.71  
TREES_PER_KG_CO2 = 1 / 21.0  

def inject_custom_css():
    st.markdown("""
        <style>
        /* --- Sidebar Navigation Font Size Fix --- */
        section[data-testid="stSidebar"] div[data-testid="stSidebarNav"] ul li a span {
            font-size: 19px !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stSidebarNav"] * { font-size: 19px !important; }
        section[data-testid="stSidebar"] div[data-testid="stSidebarNav"] ul li { padding-top: 6px !important; padding-bottom: 6px !important; }
        
        /* --- KPI Card Styles (Letting Streamlit Handle Themes natively) --- */
        .big-font { font-size:24px !important; font-weight: bold; color: #4CAF50; }
        
        .metric-card { background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50; color: var(--text-color); margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
        .peak-card { background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; border-left: 5px solid #FF9800; color: var(--text-color); margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
        .carbon-card { background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; border-left: 5px solid #00BCD4; color: var(--text-color); margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
        </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_and_calculate_kpis():
    baseline = pd.read_csv("baseline_results.csv")
    agent = pd.read_csv("agent_results.csv")
    
    b_df = baseline.groupby(["day", "hour"]).mean().reset_index()
    a_df = agent.groupby(["day", "hour"]).mean().reset_index()
    
    b_df["power_kW"] = b_df["power_W"] / 1000
    a_df["power_kW"] = a_df["power_W"] / 1000
    b_df["energy_kwh"] = b_df["power_kW"] * 1
    a_df["energy_kwh"] = a_df["power_kW"] * 1
    
    b_df["time"] = pd.to_datetime("2026-07-01") + pd.to_timedelta(b_df["day"] - 182, unit="D") + pd.to_timedelta(b_df["hour"], unit="h")
    a_df["time"] = pd.to_datetime("2026-07-01") + pd.to_timedelta(a_df["day"] - 182, unit="D") + pd.to_timedelta(a_df["hour"], unit="h")
    
    b_total_kwh = b_df["energy_kwh"].sum()
    a_total_kwh = a_df["energy_kwh"].sum()
    savings_kwh = b_total_kwh - a_total_kwh
    
    kpis = {
        "savings_inr": savings_kwh * COMMERCIAL_RATE_INR,
        "b_peak_kw": b_df["power_kW"].max(),
        "a_peak_kw": a_df["power_kW"].max(),
        "peak_reduction": b_df["power_kW"].max() - a_df["power_kW"].max(),
        "co2_avoided": savings_kwh * GRID_EMISSION_FACTOR,
        "trees": (savings_kwh * GRID_EMISSION_FACTOR) * TREES_PER_KG_CO2,
        "b_total_kwh": b_total_kwh,
        "a_total_kwh": a_total_kwh
    }
    return b_df, a_df, kpis

def render_kpi_row(kpis, pmv_threshold=0.5):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>💰 OpEx Savings</h4>
            <div class="big-font">₹{kpis['savings_inr']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="peak-card">
            <h4>⚡ Peak Demand Drop</h4>
            <div class="big-font" style="color:#FF9800;">-{kpis['peak_reduction']:,.1f} kW</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="carbon-card">
            <h4>🌳 ESG Impact</h4>
            <div class="big-font" style="color:#00BCD4;">{kpis['co2_avoided']:,.0f} kg CO₂</div>
        </div>
        """, unsafe_allow_html=True)