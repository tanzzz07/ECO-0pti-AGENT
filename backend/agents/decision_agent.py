from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
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
    print(f"Decision Agent LLM Init Warning: {e}")

decision_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an intelligent sustainability decision agent. You have received an analysis of a business's CO2 emissions and a list of suggestions from various specialized agents.\n\nYour task is to review all the provided information and synthesize it into a final, prioritized sustainability plan."),
    ("user", "Input from agents:\n{input}\n\nBased on this, provide a concise summary of the business's carbon footprint and then give exactly three prioritized, highly actionable recommendations.")
])

parser = StrOutputParser()

def run_decision_agent_safe(input_data):
    if llm:
        try:
            decision_chain = decision_prompt | llm | parser
            return decision_chain.invoke({"input": input_data})
        except Exception as e:
            print(f"Error in Decision Agent LLM: {e}")

    # Fallback synthesis when LLM is unreachable or errors out
    total = input_data.get("total_emissions", "N/A")
    breakdown = input_data.get("emissions_breakdown", {})
    suggestions = input_data.get("all_suggestions", [])
    
    clean_suggs = [str(s) for s in suggestions if s and not str(s).startswith("Error:")]
    highest_source = max(breakdown, key=breakdown.get) if breakdown else "electricity"
    
    rec_1 = clean_suggs[0] if len(clean_suggs) > 0 else f"Upgrade {highest_source} equipment to high-efficiency models."
    rec_2 = clean_suggs[1] if len(clean_suggs) > 1 else "Implement automated scheduling and smart power/route management."
    rec_3 = clean_suggs[2] if len(clean_suggs) > 2 else "Evaluate renewable energy infrastructure investments such as solar panels."

    return (
        f"**Summary of Carbon Footprint:**\n"
        f"Your estimated monthly carbon footprint is {total} kg CO₂. "
        f"The primary driver of your emissions is {highest_source}.\n\n"
        f"**Prioritized Sustainability Plan:**\n"
        f"1. **Primary Focus**: {rec_1}\n"
        f"2. **Operational Efficiency**: {rec_2}\n"
        f"3. **Long-Term Infra**: {rec_3}"
    )

run_decision_agent = RunnableLambda(run_decision_agent_safe)