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
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN", "dummy_key")
)
llm = ChatHuggingFace(llm=llm_endpoint)

optimizer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an intelligent sustainability optimizer. Your task is to analyze the information and provide a single, prioritized suggestion for the business."),
    ("user", "Context:\n- Total monthly CO₂ emissions: {total_emissions} kg\n- Emissions breakdown by source: {emissions_breakdown}\n- Raw suggestions from specialized agents: {all_suggestions}\n\nBased on the emissions data and the provided suggestions, identify the most cost-effective and highest-impact action the business can take immediately. Your response should be a single, concise recommendation (e.g., \"The highest-impact first step is to upgrade all lighting to energy-efficient LEDs, as this will reduce your largest source of emissions.\").")
])

def run_optimizer_agent(state: dict) -> dict:
    total_emissions = state["total_emissions"]
    emissions_breakdown = state["emissions_breakdown"]
    all_suggestions = state["all_suggestions"]
    
    formatted_breakdown = ", ".join([f"{source}: {emissions} kg" for source, emissions in emissions_breakdown.items()])
    formatted_suggestions = "\n".join(all_suggestions)
    
    chain = optimizer_prompt | llm
    optimizer_output = chain.invoke({
        "total_emissions": total_emissions,
        "emissions_breakdown": formatted_breakdown,
        "all_suggestions": formatted_suggestions
    }).content
    
    state["optimizer_output"] = optimizer_output
    
    return state