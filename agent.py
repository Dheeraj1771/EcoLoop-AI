import csv
import os

from dotenv import load_dotenv
from openai import OpenAI
from pyenergyplus.api import EnergyPlusAPI

# --- 1. SETUP & AUTHENTICATION ---
load_dotenv()
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

print("Patching IDF for Autonomous AI simulation...")
with open("assets/baseline_building.idf", "r") as f:
    idf_lines = f.readlines()

with open("assets/baseline_building_patched.idf", "w") as f:
    for line in idf_lines:
        if "!- Run Simulation for Weather File Run Periods" in line:
            line = "  Yes,                     !- Run Simulation for Weather File Run Periods\n"
        if "!- Run Simulation for Sizing Periods" in line:
            line = "  No,                      !- Run Simulation for Sizing Periods\n"
        if "!- Begin Month" in line: line = "  7,                       !- Begin Month\n"
        if "!- Begin Day of Month" in line: line = "  1,                       !- Begin Day of Month\n"
        if "!- End Month" in line: line = "  7,                       !- End Month\n"
        if "!- End Day of Month" in line: line = "  31,                      !- End Day of Month\n"
        f.write(line)
    
    f.write("\n")
    f.write("Output:Variable, *, Zone Mean Air Temperature, detailed;\n")
    f.write("Output:Variable, *, Zone Thermal Comfort Fanger Model PMV, detailed;\n")
    f.write("Output:Meter, Electricity:Facility, detailed;\n")

# --- 2. STATE & AI TOOLS ---
current_state = {"temperature": 24.0, "pmv": 0.0, "power": 0.0, "hour": 0}
ai_setpoint = 24.0

def set_temperature(new_setpoint: float):
    global ai_setpoint
    new_setpoint = max(21.0, min(new_setpoint, 28.0))
    ai_setpoint = new_setpoint

def ask_ai_for_setpoint():
    prompt = f"""You are an elite HVAC optimization AI for a commercial office.
    Current Temp: {current_state['temperature']}C
    Comfort (PMV): {current_state['pmv']} (Ideal is 0.0, max acceptable is 0.5)
    Power Draw: {current_state['power']}W
    
    RULES:
    - If PMV < 0 (people are cool), RAISE the setpoint to save power.
    - If PMV > 0.5 (people are hot), LOWER the setpoint.
    - Respond ONLY with a float number between 21.0 and 28.0 representing the new cooling setpoint. Do not add text."""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0, 
            max_tokens=10
        )
        decision = float(response.choices[0].message.content.strip())
        set_temperature(decision)
    except (ValueError, AttributeError, IndexError) as e:
        print(f"[AI ERROR] Parse failed: {e}. Maintaining {ai_setpoint}°C")

# --- 3. THE PHYSICS CALLBACK LOOP ---
api = EnergyPlusAPI()
state = api.state_manager.new_state()

api.exchange.request_variable(state, "Zone Mean Air Temperature", "CORE_ZN")
api.exchange.request_variable(state, "Zone Thermal Comfort Fanger Model PMV", "CORE_ZN")

handles = {"temp": -1, "power": -1, "pmv": -1, "actuator": -1}
agent_data = []
last_hour_checked = -1

def ai_callback(state_arg):
    global last_hour_checked, ai_setpoint
    
    if not api.exchange.api_data_fully_ready(state_arg) or api.exchange.warmup_flag(state_arg):
        return

    if handles["temp"] == -1: handles["temp"] = api.exchange.get_variable_handle(state_arg, "Zone Mean Air Temperature", "CORE_ZN")
    if handles["pmv"] == -1: handles["pmv"] = api.exchange.get_variable_handle(state_arg, "Zone Thermal Comfort Fanger Model PMV", "CORE_ZN")
    
    if handles["power"] == -1:
        h_meter_fac = api.exchange.get_meter_handle(state_arg, "Electricity:Facility")
        h_meter_hvac = api.exchange.get_meter_handle(state_arg, "Electricity:HVAC")
        if h_meter_fac != -1: handles["power"] = h_meter_fac
        elif h_meter_hvac != -1: handles["power"] = h_meter_hvac
        else: handles["power"] = -2
        
    if handles["actuator"] == -1: handles["actuator"] = api.exchange.get_actuator_handle(state_arg, "Zone Temperature Control", "Cooling Setpoint", "CORE_ZN")

    if handles["temp"] == -1: return

    temp = api.exchange.get_variable_value(state_arg, handles["temp"])
    pmv = api.exchange.get_variable_value(state_arg, handles["pmv"]) if handles["pmv"] != -1 else 0.0
    
    power = 0.0
    if handles["power"] > -1:
        power = api.exchange.get_meter_value(state_arg, handles["power"])

    if pmv == 0.0 and temp > 0:
        pmv = (temp - 24.0) * 0.5

    day = api.exchange.day_of_year(state_arg)
    hour = api.exchange.hour(state_arg)
    
    if day < 182 or day > 212:
        return

    # --- LIVE TELEMETRY TRIGGER ---
    if hour != last_hour_checked:
        last_hour_checked = hour
        current_state.update({"temperature": round(temp, 2), "pmv": round(pmv, 2), "power": round(power, 2), "hour": hour})
        
        if hour < 7 or hour >= 19:
            ai_setpoint = 28.0
            mode = "NIGHT SETBACK (Python)"
        else:
            ask_ai_for_setpoint()
            mode = "AI REASONING (LLM)"
            
        # LIVE CONSOLE FEED: Prints telemetry instantly every hour
        power_kw = round(power / 1000, 2)
        print(f"[Day {day:02d} | Hr {hour:02d}:00] Mode: {mode} | Temp: {temp:.2f}°C | PMV: {pmv:.2f} | Power: {power_kw} kW | Setpoint: {ai_setpoint}°C")
        
    if handles["actuator"] != -1:
        api.exchange.set_actuator_value(state_arg, handles["actuator"], ai_setpoint)

    agent_data.append({
        "day": day, "hour": hour, "minute": api.exchange.minutes(state_arg),
        "temperature_C": round(temp, 2), "power_W": round(power, 2), "pmv": round(pmv, 2),
        "ai_setpoint_C": ai_setpoint
    })

api.runtime.callback_end_zone_timestep_after_zone_reporting(state, ai_callback)

print("Booting AI Agent. Live telemetry feed is online...")
api.runtime.run_energyplus(state, ['-w', 'assets/weather.epw', '-d', 'ep_outputs', 'assets/baseline_building_patched.idf'])

csv_file = "agent_results.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["day", "hour", "minute", "temperature_C", "power_W", "pmv", "ai_setpoint_C"])
    writer.writeheader()
    writer.writerows(agent_data)

print(f"Success! Agent performance logged to {csv_file}")