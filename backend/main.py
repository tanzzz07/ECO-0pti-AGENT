
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
from models import db, User, Analysis
from flask_jwt_extended import get_jwt_identity
from auth_utils import admin_required
from flask import send_file
from pdf_gen import generate_report
from models import User, Analysis

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from models import db, User
# Absolute imports from the agents directory
from agents.electricity_agent import run_electricity_agent
from agents.transport_agent import run_transport_agent
from agents.fuel_agent import run_fuel_agent
from agents.greeninfra_agent import run_greeninfra_agent
from agents.optimizer_agent import run_optimizer_agent
from agents.decision_agent import run_decision_agent
from flask import send_file
from pdf_generator import generate_report

from models import User, Analysis

# Serve static files from the frontend directory
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecoopti.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["JWT_SECRET_KEY"] = (
    "eco-opti-agent-super-secure-jwt-secret-key-for-development-2026"
)

db.init_app(app)

jwt = JWTManager(app)

with app.app_context():
    db.create_all()
CORS(app)


@app.route('/ping')
def ping():
    return {"status": "ok"}
@app.route('/')
def index():
    return send_from_directory(
        app.static_folder,
        'login.html'
    )
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


@app.route('/register', methods=['POST'])
def register():

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({
            "error": "Missing fields"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "error": "User already exists"
        }), 400

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful"
    }), 201
@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    
    print("EMAIL RECEIVED:", email)
    
    

    user = User.query.filter_by(
    email=email).first()
    
    print("USER FOUND:", user)

    if not user:
        return jsonify({
            "error": "Invalid credentials"
        }), 401
    
    print(
        "PASSWORD CHECK:",
        check_password_hash(user.password_hash, password)
    )    

    if not check_password_hash(
        user.password_hash,
        password
    ):
        return jsonify({
            "error": "Invalid credentials"
        }), 401

    token = create_access_token(
        identity=str(user.id)
    )

    return jsonify({
    "access_token": token,
    "username": user.username,
    "role": user.role
}), 200
    
    
@app.route('/analyze', methods=['POST'])
@jwt_required()
def analyze():

    current_user_id = int(get_jwt_identity())

    try:

        data = request.json

        if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):

            return jsonify({
                "electricity_suggestions": [
                    "Switch to LED bulbs",
                    "Use smart power strips",
                    "Optimize AC usage"
                ],
                "transport_suggestions": [
                    "Use public transit",
                    "Carpool",
                    "Switch to electric vehicles"
                ],
                "fuel_suggestions": [
                    "Perform regular maintenance",
                    "Use alternative fuels",
                    "Optimize routing"
                ],
                "greeninfra_suggestion":
                    "Consider installing solar panels or green roofs.",

                "emissions_breakdown": {
                    "electricity": 120.5,
                    "transport": 350.2,
                    "fuel": 50.0
                },

                "total_emissions_kg_per_month": 520.7,

                "optimizer_output":
                    "The most significant source of emissions is transport. Prioritize EV transition.",

                "final_decision":
                    "Implement the suggested transport and electricity optimizations. Start with LED replacements for immediate impact."
            })

        # ----------------------------
        # Step 1: Run Agents
        # ----------------------------

        electricity_suggestions, electricity_emission = run_electricity_agent(data)

        transport_suggestions, transport_emission = run_transport_agent(data)

        fuel_suggestions, fuel_emission = run_fuel_agent(data)

        greeninfra_suggestion = run_greeninfra_agent.invoke({
            "data": data
        })

        # ----------------------------
        # Step 2: Aggregate Results
        # ----------------------------

        all_suggestions = (
            electricity_suggestions
            + transport_suggestions
            + fuel_suggestions
        )

        emissions_breakdown = {
            "electricity": electricity_emission,
            "transport": transport_emission,
            "fuel": fuel_emission
        }

        total_emissions = sum(
            emissions_breakdown.values()
        )

        # ----------------------------
        # Step 3: Optimizer
        # ----------------------------

        optimizer_state = {
            "total_emissions": total_emissions,
            "emissions_breakdown": emissions_breakdown,
            "all_suggestions": all_suggestions
        }

        optimizer_output = run_optimizer_agent(
            optimizer_state
        )["optimizer_output"]

        # ----------------------------
        # Step 4: Decision Agent
        # ----------------------------

        decision_agent_input_str = (
            f"Total emissions: {total_emissions} kg\n"
            f"Emissions breakdown: {emissions_breakdown}\n"
            f"Green Infrastructure Status: {greeninfra_suggestion}\n"
            f"All raw suggestions: {all_suggestions}\n"
            f"Optimizer's primary suggestion: {optimizer_output}"
        )

        final_decision = run_decision_agent.invoke({
            "input": decision_agent_input_str
        })

        # ----------------------------
        # Step 5: Save Analysis
        # ----------------------------

        analysis = Analysis(
            user_id=current_user_id,
            total_emissions=total_emissions,
            optimizer_output=str(optimizer_output),
            final_decision=str(final_decision)
        )

        db.session.add(analysis)
        db.session.commit()

        # ----------------------------
        # Step 6: Return Response
        # ----------------------------

        return jsonify({

            "analysis_id": analysis.id,

            "electricity_suggestions":
                electricity_suggestions,

            "transport_suggestions":
                transport_suggestions,

            "fuel_suggestions":
                fuel_suggestions,

            "greeninfra_suggestion":
                greeninfra_suggestion,

            "emissions_breakdown":
                emissions_breakdown,

            "total_emissions_kg_per_month":
                total_emissions,

            "optimizer_output":
                optimizer_output,

            "final_decision":
                final_decision

        })

    except Exception as e:

        import traceback
        traceback.print_exc()

        return jsonify({
            "error": f"Backend Error: {str(e)}"
        }), 400
    
@app.route('/history', methods=['GET'])
@jwt_required()
def history():

    user_id = int(get_jwt_identity())

    analyses = Analysis.query.filter_by(
        user_id=user_id
    ).order_by(
        Analysis.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": a.id,
            "total_emissions": a.total_emissions,
            "optimizer_output": a.optimizer_output,
            "final_decision": a.final_decision,
            "created_at": a.created_at.isoformat()
        }
        for a in analyses
    ])
    
@app.route(
    "/analysis/<int:analysis_id>/pdf",
    methods=["GET"]
)
@jwt_required()
def download_pdf(analysis_id):

    user_id = int(get_jwt_identity())

    analysis = Analysis.query.filter_by(
        id=analysis_id,
        user_id=user_id
    ).first()

    if not analysis:
        return jsonify({
            "error": "Analysis not found"
        }), 404

    user = User.query.get(user_id)

    pdf_path = (
        f"reports/generated_pdfs/"
        f"report_{analysis.id}.pdf"
    )

    generate_report(
        pdf_path,
        user,
        analysis
    )

    return send_file(
        pdf_path,
        as_attachment=True, 
        download_name=f"report_{analysis.id}.pdf"
    )    
    
@app.route('/get_all_users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():

    current_user_id = int(
        get_jwt_identity()
    )

    current_user = User.query.get(
        current_user_id
    )

    if current_user.role != "admin":

        return jsonify({
            "error": "Admin access required"
        }), 403

    users = User.query.all()

    return jsonify([
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ])
    
@app.route('/analysis/<int:analysis_id>/pdf', methods=['GET'])
@jwt_required()
def download_report(analysis_id):

    user_id = int(get_jwt_identity())

    analysis = Analysis.query.filter_by(
        id=analysis_id,
        user_id=user_id
    ).first()

    if not analysis:
        return jsonify({
            "error": "Analysis not found"
        }), 404

    pdf_path = f"reports/report_{analysis.id}.pdf"

    generate_report(
        pdf_path,
        analysis
    )

    return send_file(
        pdf_path,
        as_attachment=True
    )    
print(app.url_map)
if __name__== '__main__':
    app.run(host="0.0.0.0", port=7860, debug=False)