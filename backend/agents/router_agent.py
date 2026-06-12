# The router logic is now handled in a simplified way within main.py,
# but here is the original function for reference if you expand to a full LangGraph graph.

def route_input(state: dict) -> str:
    """
    Decides which agent to call next based on the presence of specific keys in the input.
    """
    input_data = state.get("user_input", {})
    
    has_electricity_data = any(key in input_data for key in ["lighting_type", "number_of_ac_units", "monthly_electricity_bill"])
    has_fuel_data = any(key in input_data for key in ["uses_diesel_generator", "uses_lpg_or_propane"])
    has_transport_data = any(key in input_data for key in ["number_of_diesel_vehicles", "average_km_per_vehicle_per_day"])
    has_greeninfra_data = any(key in input_data for key in ["uses_solar_panels", "uses_energy_efficient_devices"])

    agents_to_run = []
    if has_electricity_data:
        agents_to_run.append("electricity")
    if has_fuel_data:
        agents_to_run.append("fuel")
    if has_transport_data:
        agents_to_run.append("transport")
    if has_greeninfra_data:
        agents_to_run.append("green_infra")
    
    state["agents_to_run"] = agents_to_run
    return "run_agents"