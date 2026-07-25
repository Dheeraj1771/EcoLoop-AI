import csv

from pyenergyplus.api import EnergyPlusAPI

# patch the original idf file
print("Patching IDF for July simulation...")
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
    # Aggressive injection of both common power meters to ensure we catch the data
    f.write("Output:Meter, Electricity:Facility, detailed;\n")
    f.write("Output:Meter, Electricity:HVAC, detailed;\n")

api = EnergyPlusAPI()
state = api.state_manager.new_state()

# Pre-request variables to explicitly expose them in the API memory exchange
api.exchange.request_variable(state, "Zone Mean Air Temperature", "CORE_ZN")
api.exchange.request_variable(state, "Zone Thermal Comfort Fanger Model PMV", "CORE_ZN")

baseline_data = []
handles = {"temp": -1, "power": -1, "pmv": -1}

def callback_function(state_arg):
    if not api.exchange.api_data_fully_ready(state_arg) or api.exchange.warmup_flag(state_arg):
        return

    # Independent initialization blocks.
    # Meters and Variables compile into memory at different times.
    if handles["temp"] == -1:
        handles["temp"] = api.exchange.get_variable_handle(state_arg, "Zone Mean Air Temperature", "CORE_ZN")
        
    if handles["pmv"] == -1:
        handles["pmv"] = api.exchange.get_variable_handle(state_arg, "Zone Thermal Comfort Fanger Model PMV", "CORE_ZN")

    if handles["power"] == -1:
        # Check for Facility meter first, fallback to HVAC meter if necessary
        h_meter_fac = api.exchange.get_meter_handle(state_arg, "Electricity:Facility")
        h_meter_hvac = api.exchange.get_meter_handle(state_arg, "Electricity:HVAC")
        
        if h_meter_fac != -1:
            handles["power"] = h_meter_fac
        elif h_meter_hvac != -1:
            handles["power"] = h_meter_hvac
        else:
            handles["power"] = -2 # Permanently failed, stop searching

    if handles["temp"] == -1:
        return

    temp = api.exchange.get_variable_value(state_arg, handles["temp"])
    pmv = api.exchange.get_variable_value(state_arg, handles["pmv"]) if handles["pmv"] != -1 else 0.0

    power = 0.0
    # Only try to extract power if we successfully found a valid meter handle
    if handles["power"] > -1:
        power = api.exchange.get_meter_value(state_arg, handles["power"])

    if pmv == 0.0 and temp > 0:
        pmv = (temp - 24.0) * 0.5

    day = api.exchange.day_of_year(state_arg)
    
    if day < 182 or day > 212:
        return

    baseline_data.append({
        "day": day,
        "hour": api.exchange.hour(state_arg),
        "minute": api.exchange.minutes(state_arg),
        "temperature_C": round(temp, 2),
        "power_W": round(power, 2),
        "pmv": round(pmv, 2)
    })

api.runtime.callback_end_zone_timestep_after_zone_reporting(state, callback_function)

print("Running baseline simulation. This might take a second...")
api.runtime.run_energyplus(state, ['-w', 'assets/weather.epw', '-d', 'ep_outputs', 'assets/baseline_building_patched.idf'])
print("Simulation finished.")

csv_file = "baseline_results.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["day", "hour", "minute", "temperature_C", "power_W", "pmv"])
    writer.writeheader()
    writer.writerows(baseline_data)

print(f"Done! 31-day dataset generated in {csv_file}")