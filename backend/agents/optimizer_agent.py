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
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN", "dummy_key")
    )
    llm = ChatHuggingFace(llm=llm_endpoint)
except Exception as e:
    print(f"Optimizer Agent LLM Init Warning: {e}")

optimizer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an intelligent sustainability optimizer. Your task is to analyze the information and provide a single, prioritized suggestion for the business."),
    ("user", "Context:\n- Total monthly CO₂ emissions: {total_emissions} kg\n- Emissions breakdown by source: {emissions_breakdown}\n- Raw suggestions from specialized agents: {all_suggestions}\n\nBased on the emissions data and the provided suggestions, identify the most cost-effective and highest-impact action the business can take immediately. Your response should be a single, concise recommendation.")
])

def run_optimizer_agent(state: dict) -> dict:
    total_emissions = state["total_emissions"]
    emissions_breakdown = state["emissions_breakdown"]
    all_suggestions = state["all_suggestions"]
    
    formatted_breakdown = ", ".join([f"{source}: {emissions} kg" for source, emissions in emissions_breakdown.items()])
    formatted_suggestions = "\n".join([str(s) for s in all_suggestions if s and not str(s).startswith("Error:")])
    
    optimizer_output = ""
    if llm:
        try:
            chain = optimizer_prompt | llm
            res = chain.invoke({
                "total_emissions": total_emissions,
                "emissions_breakdown": formatted_breakdown,
                "all_suggestions": formatted_suggestions
            })
            optimizer_output = res.content if hasattr(res, "content") else str(res)
        except Exception as e:
            print(f"Error in Optimizer Agent LLM: {e}")
            optimizer_output = ""
            
    if not optimizer_output:
        highest_source = max(emissions_breakdown, key=emissions_breakdown.get) if emissions_breakdown else "electricity"
        highest_val = emissions_breakdown.get(highest_source, 0)
        optimizer_output = (
            f"The highest-impact priority is to focus on reducing {highest_source} emissions ({highest_val} kg CO₂/month), "
            f"which accounts for the largest share of your total footprint ({total_emissions} kg CO₂/month)."
        )
    
    state["optimizer_output"] = optimizer_output
    return state