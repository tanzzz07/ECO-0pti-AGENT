from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

class ElectricitySuggestions(BaseModel):
    suggestions: list[str] = Field(..., description="A list of three actionable suggestions for reducing electricity consumption.")

llm_endpoint = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    task="text-generation",
    max_new_tokens=512,
    do_sample=False,
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN", "dummy_key")
)
llm = ChatHuggingFace(llm=llm_endpoint)

parser = PydanticOutputParser(pydantic_object=ElectricitySuggestions)

electricity_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an energy optimization assistant. You must reply strictly in JSON format.\n{format_instructions}"),
    ("user", "The user provides:\n- Lighting type: {lighting_type}\n- Light usage hours/day: {light_usage_hours_per_day}\n- AC units: {number_of_ac_units}\n- AC usage hours/day: {ac_usage_hours_per_day}\n- Monthly electricity bill: ₹{monthly_electricity_bill}\n- Uses solar panels: {uses_solar_panels}\n- Uses energy efficient devices: {uses_energy_efficient_devices}\nThe estimated electricity CO2 emission is {estimated_co2_emission} kg/month.\n\nProvide exactly three actionable suggestions to optimize energy usage and reduce this emission.")
])

def run_electricity_agent(input_data):
    LED_WATTAGE = 10
    AC_WATTAGE_KW = 1.5
    num_lights = 10
    light_usage_hours = input_data.get("light_usage_hours_per_day", 0)
    ac_units = input_data.get("number_of_ac_units", 0)
    ac_usage_hours = input_data.get("ac_usage_hours_per_day", 0)
    
    monthly_kwh_lights = (num_lights * LED_WATTAGE * light_usage_hours * 30) / 1000
    monthly_kwh_ac = (ac_units * AC_WATTAGE_KW * ac_usage_hours * 30)
    total_kwh_monthly = monthly_kwh_lights + monthly_kwh_ac
    
    electricity_emission = round(total_kwh_monthly * 0.82, 2)
    input_data["estimated_co2_emission"] = electricity_emission
    
    try:
        _prompt = electricity_prompt.partial(format_instructions=parser.get_format_instructions())
        chain = _prompt | llm | parser
        response = chain.invoke(input_data)
        
        if response and hasattr(response, "suggestions"):
            return response.suggestions, electricity_emission
        else:
            print("Warning: LLM returned an empty response for electricity_agent.")
            return ["No suggestions available due to an empty LLM response."], electricity_emission
            
    except Exception as e:
        print(f"Error in Electricity Agent: {e}")
        return [f"Error: {str(e)}"], electricity_emission