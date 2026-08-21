# pyrefly: ignore [missing-import]
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

llm = None
try:
    llm_endpoint = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-72B-Instruct",
        task="text-generation",
        max_new_tokens=512,
        do_sample=False,
        timeout=4.0,
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN", "dummy_key")
    )
    llm = ChatHuggingFace(llm=llm_endpoint)
except Exception as e:
    print(f"Electricity Agent LLM Init Warning: {e}")

electricity_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an energy optimization assistant. "
        "Provide exactly three actionable suggestions "
        "to reduce electricity consumption."
    ),
    (
        "user",
        "The user provides:\n"
        "- Lighting type: {lighting_type}\n"
        "- Light usage hours/day: {light_usage_hours_per_day}\n"
        "- AC units: {number_of_ac_units}\n"
        "- AC usage hours/day: {ac_usage_hours_per_day}\n"
        "- Monthly electricity bill: ₹{monthly_electricity_bill}\n"
        "- Uses solar panels: {uses_solar_panels}\n"
        "- Uses energy efficient devices: {uses_energy_efficient_devices}\n\n"
        "The estimated electricity CO2 emission is "
        "{estimated_co2_emission} kg/month.\n\n"
        "Provide exactly three actionable suggestions."
    )
])


def run_electricity_agent(input_data):
    input_data.setdefault("lighting_type", "LED")

    LED_WATTAGE = 10
    AC_WATTAGE_KW = 1.5
    num_lights = 10

    light_usage_hours = input_data.get("light_usage_hours_per_day", 0)
    ac_units = input_data.get("number_of_ac_units", 0)
    ac_usage_hours = input_data.get("ac_usage_hours_per_day", 0)

    monthly_kwh_lights = (num_lights * LED_WATTAGE * light_usage_hours * 30) / 1000
    monthly_kwh_ac = ac_units * AC_WATTAGE_KW * ac_usage_hours * 30
    total_kwh_monthly = monthly_kwh_lights + monthly_kwh_ac

    electricity_emission = round(total_kwh_monthly * 0.82, 2)
    input_data["estimated_co2_emission"] = electricity_emission

    if llm:
        try:
            chain = electricity_prompt | llm
            response = chain.invoke(input_data)

            response_text = ""
            if hasattr(response, "content"):
                response_text = response.content
            else:
                response_text = str(response)

            suggestions = [
                line.strip("-• ")
                for line in response_text.split("\n")
                if line.strip()
            ]

            if len(suggestions) >= 3:
                return suggestions[:3], electricity_emission
        except Exception as e:
            print(f"Error in Electricity Agent LLM: {e}")

    return [
        "Switch all lighting fixtures to energy-efficient LED technology",
        "Install smart thermostats and schedule AC usage during occupancy only",
        "Deploy smart power strips to eliminate phantom standby loads"
    ], electricity_emission