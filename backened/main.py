
# from flask import Flask, request, jsonify
# from langgraph.graph import StateGraph, END
# import operator
# from typing import TypedDict, Annotated

# # Relative imports from the backend package
# from .agents.electricity_agent import run_electricity_agent
# from .agents.transport_agent import run_transport_agent
# from .agents.fuel_agent import run_fuel_agent
# from .agents.greeninfra_agent import run_greeninfra_agent
# from .agents.optimizer_agent import run_optimizer_agent
# from .agents.decision_agent import run_decision_agent

# app = Flask(__name__)

# # Define the state of our graph (This is for a more advanced LangGraph setup)
# class AgentState(TypedDict):
#     user_input: dict
#     agents_to_run: list[str]
#     electricity_suggestions: Annotated[list, operator.add]
#     transport_suggestions: Annotated[list, operator.add]
#     fuel_suggestions: Annotated[list, operator.add]
#     greeninfra_suggestion: str
#     all_suggestions: Annotated[list, operator.add]
#     electricity_emission: float
#     transport_emission: float
#     fuel_emission: float
#     total_emissions: float
#     emissions_breakdown: dict
#     optimizer_output: str
#     final_decision: str

# # In this Flask app, we'll use a simplified sequential flow
# # instead of a complex LangGraph state machine for simplicity.

# @app.route('/analyze', methods=['POST'])
# def analyze():
#     data = request.json
    
#     # Step 1: Run specialized agents sequentially and collect their outputs
#     electricity_suggestions, electricity_emission = run_electricity_agent(data)
#     transport_suggestions, transport_emission = run_transport_agent(data)
#     fuel_suggestions, fuel_emission = run_fuel_agent(data)
#     greeninfra_suggestion = run_greeninfra_agent.invoke({"data":data})
    
#     # Step 2: Aggregate data for higher-level agents
#     all_suggestions = electricity_suggestions + transport_suggestions + fuel_suggestions
#     emissions_breakdown = {
#         "electricity": electricity_emission,
#         "transport": transport_emission,
#         "fuel": fuel_emission
#     }
#     total_emissions = sum(emissions_breakdown.values())

#     # Step 3: Run the Optimizer Agent
#     optimizer_state = {
#         "total_emissions": total_emissions,
#         "emissions_breakdown": emissions_breakdown,
#         "all_suggestions": all_suggestions
#     }
#     optimizer_output = run_optimizer_agent(optimizer_state)["optimizer_output"]

#     # Step 4: Run the Decision Agent
#     decision_agent_input_str = (
#         f"Total emissions: {total_emissions} kg\n"
#         f"Emissions breakdown: {emissions_breakdown}\n"
#         f"Green Infrastructure Status: {greeninfra_suggestion}\n"
#         f"All raw suggestions: {all_suggestions}\n"
#         f"Optimizer's primary suggestion: {optimizer_output}"
#     )
#     final_decision = run_decision_agent.invoke({"input": decision_agent_input_str})

#     # Step 5: Return the final JSON response
#     return jsonify({
#         # "electricity_suggestions": electricity_suggestions,
#         # "transport_suggestions": transport_suggestions,
#         # "fuel_suggestions": fuel_suggestions,
#         # "greeninfra_suggestion": greeninfra_suggestion,
#         # "emissions_breakdown": emissions_breakdown,
#         # "total_emissions_kg_per_month": total_emissions,
#         "optimizer_output": optimizer_output,
#         "final_decision": final_decision
#     })

# if __name__== '__main__':
#     app.run(debug=True)
import os
from flask import Flask, request, jsonify, send_from_directory
from langgraph.graph import StateGraph, END
import operator
from typing import TypedDict, Annotated
from flask_cors import CORS

# Absolute imports from the agents directory
from agents.electricity_agent import run_electricity_agent
from agents.transport_agent import run_transport_agent
from agents.fuel_agent import run_fuel_agent
from agents.greeninfra_agent import run_greeninfra_agent
from agents.optimizer_agent import run_optimizer_agent
from agents.decision_agent import run_decision_agent

# Serve static files from the frontend directory
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Define the state of our graph (This is for a more advanced LangGraph setup)
class AgentState(TypedDict):
    user_input: dict
    agents_to_run: list[str]
    electricity_suggestions: Annotated[list, operator.add]
    transport_suggestions: Annotated[list, operator.add]
    fuel_suggestions: Annotated[list, operator.add]
    greeninfra_suggestion: str
    all_suggestions: Annotated[list, operator.add]
    electricity_emission: float
    transport_emission: float
    fuel_emission: float
    total_emissions: float
    emissions_breakdown: dict
    optimizer_output: str
    final_decision: str

# In this Flask app, we'll use a simplified sequential flow
# instead of a complex LangGraph state machine for simplicity.

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json

        if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
            # Mock response when API key is missing
            return jsonify({
            "electricity_suggestions": ["Switch to LED bulbs", "Use smart power strips", "Optimize AC usage"],
            "transport_suggestions": ["Use public transit", "Carpool", "Switch to electric vehicles"],
            "fuel_suggestions": ["Perform regular maintenance", "Use alternative fuels", "Optimize routing"],
            "greeninfra_suggestion": "Consider installing solar panels or green roofs.",
            "emissions_breakdown": {"electricity": 120.5, "transport": 350.2, "fuel": 50.0},
            "total_emissions_kg_per_month": 520.7,
            "optimizer_output": "The most significant source of emissions is transport. Prioritize EV transition.",
            "final_decision": "Implement the suggested transport and electricity optimizations. **Action:** Start with LED replacements. **Impact:** Immediate reduction in power consumption."
        })
        
        # UI keys are already correctly named. No mapping needed.
        
        # Step 1: Run specialized agents sequentially and collect their outputs
        electricity_suggestions, electricity_emission = run_electricity_agent(data)
        transport_suggestions, transport_emission = run_transport_agent(data)
        fuel_suggestions, fuel_emission = run_fuel_agent(data)
        greeninfra_suggestion = run_greeninfra_agent.invoke({"data":data})
        
        # Step 2: Aggregate data for higher-level agents
        all_suggestions = electricity_suggestions + transport_suggestions + fuel_suggestions
        emissions_breakdown = {
            "electricity": electricity_emission,
            "transport": transport_emission,
            "fuel": fuel_emission
        }
        total_emissions = sum(emissions_breakdown.values())

        try:
            # Step 3: Run the Optimizer Agent
            optimizer_state = {
                "total_emissions": total_emissions,
                "emissions_breakdown": emissions_breakdown,
                "all_suggestions": all_suggestions
            }
            optimizer_output = run_optimizer_agent(optimizer_state)["optimizer_output"]

            # Step 4: Run the Decision Agent
            decision_agent_input_str = (
                f"Total emissions: {total_emissions} kg\n"
                f"Emissions breakdown: {emissions_breakdown}\n"
                f"Green Infrastructure Status: {greeninfra_suggestion}\n"
                f"All raw suggestions: {all_suggestions}\n"
                f"Optimizer's primary suggestion: {optimizer_output}"
            )
            final_decision = run_decision_agent.invoke({"input": decision_agent_input_str})
        except Exception as e:
            print(f"Error in main LLM chain: {e}")
            return jsonify({"error": str(e)}), 400

        # Step 5: Return the final JSON response with ALL keys
        return jsonify({
            "electricity_suggestions": electricity_suggestions,
            "transport_suggestions": transport_suggestions,
            "fuel_suggestions": fuel_suggestions,
            "greeninfra_suggestion": greeninfra_suggestion,
            "emissions_breakdown": emissions_breakdown,
            "total_emissions_kg_per_month": total_emissions,
            "optimizer_output": optimizer_output,
            "final_decision": final_decision
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Backend Error: {str(e)}"}), 400

if __name__== '__main__':
    app.run(host="0.0.0.0", port=7860, debug=False)