from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

class FuelSuggestions(BaseModel):
    suggestions: list[str] = Field(..., description="A list of three actionable suggestions for reducing emissions from fuel usage.")

llm_endpoint = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    task="text-generation",
    max_new_tokens=512,
    do_sample=False,
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN", "dummy_key")
)
llm = ChatHuggingFace(llm=llm_endpoint)

parser = PydanticOutputParser(pydantic_object=FuelSuggestions)

def calculate_fuel_emissions(uses_diesel, uses_lpg):
    emission = 0
    if uses_diesel:
        emission += 200  # Arbitrary base kg for diesel generator
    if uses_lpg:
        emission += 150  # Arbitrary base kg for LPG
    return float(emission)

fuel_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an industrial fuel optimization expert. You must reply strictly in JSON format.\n{format_instructions}"),
    ("user", "The user provides the following fuel usage details:\n- Uses Diesel Generator: {uses_diesel}\n- Uses LPG/Propane: {uses_lpg}\nThe estimated fuel CO2 emission is {estimated_fuel_emission} kg/month.\n\nProvide exactly three actionable suggestions to reduce fuel-based emissions.")
])

def run_fuel_agent(input_data):
    uses_diesel = input_data.get("uses_diesel_generator", False)
    uses_lpg = input_data.get("uses_lpg_or_propane", False)
    
    fuel_emission = calculate_fuel_emissions(uses_diesel, uses_lpg)
    input_data["estimated_fuel_emission"] = fuel_emission
    input_data["uses_diesel"] = uses_diesel
    input_data["uses_lpg"] = uses_lpg
    
    try:
        _prompt = fuel_prompt.partial(format_instructions=parser.get_format_instructions())
        chain = _prompt | llm | parser
        response = chain.invoke(input_data)
        
        if response and hasattr(response, "suggestions"):
            return response.suggestions, fuel_emission
        else:
            return ["No fuel suggestions available."], fuel_emission
            
    except Exception as e:
        print(f"Error in Fuel Agent: {e}")
        return [f"Error: {str(e)}"], fuel_emission