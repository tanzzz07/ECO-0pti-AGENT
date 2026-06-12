from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()


llm_endpoint = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    task="text-generation",
    max_new_tokens=512,
    do_sample=False,
    huggingfacehub_api_token=os.getenv(
        "HUGGINGFACEHUB_API_TOKEN",
        "dummy_key"
    )
)

llm = ChatHuggingFace(llm=llm_endpoint)


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

    light_usage_hours = input_data.get(
        "light_usage_hours_per_day",
        0
    )

    ac_units = input_data.get(
        "number_of_ac_units",
        0
    )

    ac_usage_hours = input_data.get(
        "ac_usage_hours_per_day",
        0
    )

    monthly_kwh_lights = (
        num_lights *
        LED_WATTAGE *
        light_usage_hours *
        30
    ) / 1000

    monthly_kwh_ac = (
        ac_units *
        AC_WATTAGE_KW *
        ac_usage_hours *
        30
    )

    total_kwh_monthly = (
        monthly_kwh_lights +
        monthly_kwh_ac
    )

    electricity_emission = round(
        total_kwh_monthly * 0.82,
        2
    )

    input_data["estimated_co2_emission"] = electricity_emission

    try:

        chain = electricity_prompt | llm

        response = chain.invoke(input_data)

        print(
            f"Electricity Agent LLM Response: {response}"
        )

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

        return [
            "Switch to LED lighting",
            "Use smart power strips",
            "Reduce AC usage during peak hours"
        ], electricity_emission

    except Exception as e:

        print(
            f"Error in Electricity Agent: {e}"
        )

        return [
            "Switch to LED lighting",
            "Use smart power strips",
            "Reduce AC usage during peak hours"
        ], electricity_emission