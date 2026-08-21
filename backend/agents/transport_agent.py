from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
import os
from dotenv import load_dotenv

load_dotenv()


class TransportSuggestions(BaseModel):
    suggestions: list[str] = Field(
        ...,
        description="A list of three actionable suggestions for reducing transport-related emissions."
    )


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
    print(f"Transport Agent LLM Init Warning: {e}")

parser = PydanticOutputParser(pydantic_object=TransportSuggestions)


def calculate_transport_emissions(num_vehicles, avg_km_per_day):
    EMISSION_FACTOR_KG_PER_KM = 0.12
    days_in_month = 30
    total_km = num_vehicles * avg_km_per_day * days_in_month
    return round(total_km * EMISSION_FACTOR_KG_PER_KM, 2)


transport_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a transportation and logistics optimization assistant. "
        "Provide exactly three actionable suggestions."
    ),
    (
        "user",
        "The user provides the following transportation details:\n"
        "- Number of vehicles: {num_vehicles}\n"
        "- Average KM per vehicle per day: {avg_km_per_day}\n"
        "The estimated transportation CO2 emission is "
        "{estimated_transport_emission} kg/month.\n\n"
        "Provide exactly three actionable suggestions "
        "to reduce transportation emissions."
    )
])


def run_transport_agent(input_data):
    num_vehicles = input_data.get("number_of_diesel_vehicles", 0)
    avg_km_per_day = input_data.get("average_km_per_vehicle_per_day", 0)

    transport_emission = calculate_transport_emissions(num_vehicles, avg_km_per_day)

    input_data["estimated_transport_emission"] = transport_emission
    input_data["num_vehicles"] = num_vehicles
    input_data["avg_km_per_day"] = avg_km_per_day

    if llm:
        try:
            chain = transport_prompt | llm
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
                return suggestions[:3], transport_emission
        except Exception as e:
            print(f"Error in Transport Agent LLM: {e}")

    return [
        "Optimize vehicle routes and consolidate deliveries to reduce daily mileage",
        "Enforce strict anti-idling policies and schedule preventative maintenance",
        "Explore fleet electrification or hybrid alternatives for high-frequency routes"
    ], transport_emission