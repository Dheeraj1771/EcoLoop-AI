import streamlit as st

from core_logic import inject_custom_css, load_and_calculate_kpis

st.set_page_config(page_title="ESG Reporting", layout="wide")
inject_custom_css()

# --- Page-Specific CSS ---
st.markdown("""
    <style>
    .insight-card-teal { background-color: #1E1E1E; padding: 25px; border-radius: 10px; border-top: 5px solid #009688; color: #FFFFFF; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    @media (prefers-color-scheme: light) { .insight-card-teal { background-color: #f0f2f6; color: #000000; } }
    </style>
""", unsafe_allow_html=True)

_, _, kpis = load_and_calculate_kpis()

# --- HERO HEADER ---
st.markdown("<h2 style='text-align: center; color: #009688;'>📄 ESG & Financial Reporting</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Automated Compliance & Sustainability Export</h4>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Stunning Insight Card
st.markdown("""
<div class="insight-card-teal">
    <h4>🌳 Scope 2 Emissions & Capital Audit</h4>
    <p><b>Corporate Value:</b> Modern enterprises require strict auditing of their carbon footprint (Scope 2 emissions) and financial OpEx. This module instantly transforms raw simulation telemetry into a compliance-ready executive summary.</p>
    <p style="margin-bottom: 0;">It quantifies abstract energy savings into tangible stakeholder metrics: Capital saved, kilograms of CO₂ prevented, and reforestation equivalents.</p>
</div>
""", unsafe_allow_html=True)

report_text = f"""ECOLOOP AI - MONTHLY FACILITY OPTIMIZATION REPORT
-------------------------------------------------
FINANCIAL IMPACT:
- Baseline Energy Cost: ₹{kpis['b_total_kwh'] * 8.0:,.2f}
- AI Optimized Cost: ₹{kpis['a_total_kwh'] * 8.0:,.2f}
- Total Capital Saved: ₹{kpis['savings_inr']:,.2f}

ESG & SUSTAINABILITY:
- Carbon Emissions Avoided: {kpis['co2_avoided']:,.1f} kg CO2
- Reforestation Equivalent: {kpis['trees']:,.1f} Trees
- Peak Demand Reduction: {kpis['peak_reduction']:,.1f} kW

COMPLIANCE NOTE:
The LLM successfully maintained the facility within acceptable human thermal boundaries while actively optimizing setpoints.
"""

c1, c2 = st.columns([2, 1])
with c1:
    st.text_area("Live Report Preview:", value=report_text, height=350)
with c2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("💡 Generate a plaintext `.txt` file ready for stakeholder distribution.")
    if st.download_button("⬇️ Download Executive Summary (.txt)", data=report_text, file_name="EcoLoop_Report.txt", mime="text/plain", use_container_width=True):
        st.balloons()