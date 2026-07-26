import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from core_logic import COMMERCIAL_RATE_INR, inject_custom_css, load_and_calculate_kpis

st.set_page_config(page_title="AI Manager", layout="wide")
inject_custom_css()

# --- Page-Specific CSS ---
st.markdown("""
    <style>
    .insight-card-orange { 
        background-color: var(--secondary-background-color); 
        padding: 25px; 
        border-radius: 10px; 
        border-top: 5px solid #FF9800; 
        color: var(--text-color); 
        margin-bottom: 25px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
    }
    </style>
""", unsafe_allow_html=True)

load_dotenv()
client = OpenAI(api_key=os.environ.get("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
b_df, a_df, kpis = load_and_calculate_kpis()

# --- HERO HEADER ---
st.markdown("<h2 style='text-align: center; color: #FF9800;'>💬 AI Facility Manager</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Llama-3.1-8B Interactive Codebase & Telemetry Agent</h4>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Stunning Insight Card
st.markdown("""
<div class="insight-card-orange">
    <h4>🧠 Retrieval-Augmented Generation (RAG) Console</h4>
    <p><b>System Capabilities:</b> This is not a generic chatbot. It is a context-aware AI agent with direct memory access to both the facility's daily data ledger and the underlying Python control logic.</p>
    <p style="margin-bottom: 0;"><b>Judge Challenge:</b> Ask it for exact Rupee savings on a specific date (e.g., <i>"How much did we save on July 25th?"</i>), or ask it to explain the backend code (e.g., <i>"Explain how the night setback override works in agent.py"</i>).</p>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Query telemetry data or audit the Python codebase..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    daily_merged = pd.merge(b_df, a_df, on=["day", "hour"], suffixes=("_base", "_agent"))
    daily_merged["date"] = pd.to_datetime("2026-07-01") + pd.to_timedelta(daily_merged["day"] - 182, unit="D")
    daily_summary = daily_merged.groupby(daily_merged["date"].dt.date).agg({"energy_kwh_base": "sum", "energy_kwh_agent": "sum"}).reset_index()
    daily_summary["saved_inrs"] = (daily_summary["energy_kwh_base"] - daily_summary["energy_kwh_agent"]) * COMMERCIAL_RATE_INR
    
    daily_context = "\n".join([f"- {row['date']}: Base {row['energy_kwh_base']:,.0f} kWh | AI {row['energy_kwh_agent']:,.0f} kWh | Saved ₹{row['saved_inrs']:,.0f}" for _, row in daily_summary.iterrows()])
    
    try:
        with open("agent.py", "r") as f:
            code = f.read()
    except FileNotFoundError:
        code = "agent.py codebase currently unavailable."

    system_context = f"""You are EcoLoop, an elite AI facility manager. Answer accurately based on this data:
    Total Saved: ₹{kpis['savings_inr']:,.0f} | CO2 Avoided: {kpis['co2_avoided']:,.0f} kg
    DAILY DATA: {daily_context}
    CODEBASE (agent.py): {code}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": system_context}, {"role": "user", "content": prompt}],
            temperature=0.1, max_tokens=350
        )
        ai_response = response.choices[0].message.content
    except Exception as e:  # noqa: BLE001
        ai_response = f"Communication Error: {e}"
        
    with st.chat_message("assistant"):
        st.markdown(ai_response)
    st.session_state.messages.append({"role": "assistant", "content": ai_response})