import streamlit as st

from core_logic import inject_custom_css

st.set_page_config(page_title="EcoLoop AI | Home", page_icon="🌱", layout="wide")
inject_custom_css()

# Custom inline CSS for the Home Page cards to ensure Light/Dark mode compatibility
st.markdown("""
    <style>
    .arch-card-blue { background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; border-top: 5px solid #2196F3; height: 100%; color: var(--text-color); box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    .arch-card-orange { background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; border-top: 5px solid #FF9800; height: 100%; color: var(--text-color); box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    </style>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🌱 EcoLoop AI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Autonomous Building Optimization Engineered for Honeywell</h3>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- SYSTEM STATUS BAR ---
st.markdown("### 📡 Live System Telemetry")
col1, col2, col3, col4 = st.columns(4)

def telemetry_card(icon, title, status, color):
    return f"""<div style="background-color: var(--secondary-background-color); color: var(--text-color); padding: 15px; border-radius: 8px; text-align: center; border-bottom: 3px solid {color}; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <span style="font-size: 18px;">{icon} <b>{title}:</b> {status}</span>
    </div>"""

with col1: st.markdown(telemetry_card("🟢", "System", "Online", "#4CAF50"), unsafe_allow_html=True)
with col2: st.markdown(telemetry_card("⚙️", "EnergyPlus", "Synced", "#2196F3"), unsafe_allow_html=True)
with col3: st.markdown(telemetry_card("🧠", "Llama-3.1", "Connected", "#FF9800"), unsafe_allow_html=True)
with col4: st.markdown(telemetry_card("📊", "Telemetry", "Active", "#F44336"), unsafe_allow_html=True)

st.divider()

# --- ARCHITECTURE SECTION ---
st.markdown("### 🏗️ The Hybrid Supervisory Architecture")
st.markdown("EcoLoop AI bridges the gap between Large Language Models (LLMs) and physical HVAC infrastructure safely. We do not give the AI unconstrained control. Instead, we use a hybrid approach:")
st.markdown("<br>", unsafe_allow_html=True)

colA, colB = st.columns(2)
with colA:
    st.markdown("""
    <div class="arch-card-blue">
        <h4>🛡️ Deterministic Python Layer</h4>
        <p>Enforces absolute infrastructure safety rules. During unoccupied hours (19:00 - 07:00), Python overrides the system, locking the facility into a strict 28.0°C Night Setback to guarantee zero energy waste and prevent LLM hallucinations.</p>
    </div>
    """, unsafe_allow_html=True)

with colB:
    st.markdown("""
    <div class="arch-card-orange">
        <h4>🧠 Stochastic LLM Layer</h4>
        <p>Activates during daytime operations. The Llama-3.1-8B engine analyzes real-time temperature and <b>Fanger PMV</b> comfort indices to dynamically negotiate optimal setpoints, maximizing OpEx savings while preserving human comfort.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- Platform Modules Section ---
st.markdown("### 🧭 Platform Modules")
st.markdown("Use the left sidebar navigation menu to explore the capabilities of the system.")

# Custom CSS for symmetrical, equal-height module cards
st.markdown("""
    <style>
    .module-card {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        padding: 22px;
        border-radius: 10px;
        min-height: 175px; /* Guarantees identical height across all cards */
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    .module-card-blue { border-left: 5px solid #2196F3; }
    .module-card-yellow { border-left: 5px solid #FFC107; }
    .module-card-green { border-left: 5px solid #4CAF50; }
    .module-card-red { border-left: 5px solid #E91E63; }
    .module-card h4 { margin-top: 0; margin-bottom: 10px; }
    .module-card p { margin-bottom: 0; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="module-card module-card-blue">
        <h4>📊 Executive Dashboard</h4>
        <p>View the direct correlation between AI decisions and live power draw. Includes high-level financial and ESG KPIs like monthly OpEx savings and Peak Demand Drop.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="module-card module-card-green">
        <h4>📄 ESG Reporting</h4>
        <p>Generate and download compliance-ready executive text documents detailing carbon avoidance, reforestation equivalents, and OpEx savings for stakeholders.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="module-card module-card-yellow">
        <h4>📈 Deep Dive Analytics</h4>
        <p>Validate that energy savings did not compromise human comfort using our interactive 2D PMV thermal heatmap and cumulative energy consumption charts.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="module-card module-card-red">
        <h4>💬 AI Facility Manager</h4>
        <p>Chat directly with the Llama-3.1-8B facility agent. Query specific daily savings, audit the underlying codebase, or ask for performance breakdowns.</p>
    </div>
    """, unsafe_allow_html=True)