# # backend/agents/greeninfra_agent.py

# from langchain_core.tools import tool

# @tool
# def run_greeninfra_agent(data: dict) -> str:
#     """
#     Evaluates the business's use of green infrastructure and provides suggestions to enhance sustainability.

#     Expected keys in data:
#     - uses_solar_panels (bool)
#     - uses_energy_efficient_devices (bool)

#     Returns:
#     - Recommendation string
#     """
#     solar = data.get("uses_solar_panels", False)
#     efficient_devices = data.get("uses_energy_efficient_devices", False)

#     recommendations = []

#     if solar:
#         recommendations.append("✅ The business uses solar panels. Continue to monitor efficiency and expand coverage if possible.")
#     else:
#         recommendations.append("⚠ Consider installing solar panels to reduce dependence on grid electricity and lower emissions.")

#     if efficient_devices:

#         recommendations.append("✅ The business is using energy-efficient appliances. This reduces long-term energy consumption.")
#     else:
#         recommendations.append("⚠ Upgrade to energy-efficient appliances such as LED lighting, star-rated ACs, and motors.")

#     return "\n".join(recommendations)
from langchain_core.tools import tool

@tool
def run_greeninfra_agent(data: dict) -> str:
    """
    Evaluates the business's use of green infrastructure and provides suggestions to enhance sustainability.
    """
    solar = data.get("uses_solar_panels", False)
    efficient_devices = data.get("uses_energy_efficient_devices", False)

    recommendations = []

    if solar:
        recommendations.append("✅ The business uses solar panels. Continue to monitor efficiency and expand coverage if possible.")
    else:
        recommendations.append("⚠ Consider installing solar panels to reduce dependence on grid electricity and lower emissions.")

    if efficient_devices:
        recommendations.append("✅ The business is using energy-efficient appliances. This reduces long-term energy consumption.")
    else:
        recommendations.append("⚠ Upgrade to energy-efficient appliances such as LED lighting, star-rated ACs, and motors.")

    return "\n".join(recommendations)