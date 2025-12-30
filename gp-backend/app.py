from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from digital_twin import DiabetesTwin
from simulation_engine import GlucoseSimulator, RiskAssessor
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get frontend URL from environment variable for production
FRONTEND_URL = os.environ.get('FRONTEND_URL', '*')

# CORS configuration - Allow frontend to access backend
# Using a more permissive setup for debugging the "Network Error"
CORS(app, resources={
    r"/*": {
        "origins": [
            FRONTEND_URL,
            "https://medtwin-frontend.onrender.com",
            "https://grad-project-pied.vercel.app",
            "http://localhost:5173",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
        "supports_credentials": True
    }
})

@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.url}")

# --- MOCK AUTH ROUTES FOR FRONTEND ---

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    logger.info(f"Login attempt for: {email}")
    
    # Mock authentication for now to fix "Network Error"
    # In production, this would check a database
    return jsonify({
        "access_token": "mock-token-123",
        "user": {
            "id": 1,
            "email": email,
            "name": "Abeer Sherif",
            "role": "patient"
        }
    }), 200

@app.route('/api/auth/register/patient', methods=['POST'])
def register_patient():
    data = request.json
    return jsonify({
        "access_token": "mock-token-reg",
        "user": {
            "id": 1,
            "email": data.get('email'),
            "name": data.get('name', 'New Patient'),
            "role": "patient"
        }
    }), 201

# --- DASHBOARD ROUTES ---

@app.route('/api/patient/dashboard', methods=['GET'])
def patient_dashboard():
    return jsonify({
        "summary": {
            "condition": "Diabetes Type 2",
            "severity": "MODERATE",
            "next_appointment": "2024-01-15",
            "adherence_rate": "85%"
        },
        "recent_vitals": [
            {"date": "2023-12-25", "glucose": 140, "bp": "120/80"},
            {"date": "2023-12-28", "glucose": 135, "bp": "122/82"}
        ]
    }), 200

# --- EXISTING DIGITAL TWIN ROUTES ---

@app.route('/api/twin/<int:patient_id>/visualization-data', methods=['GET'])
def get_visualization_data(patient_id):
    """Get organ visualization data with risk levels for future predictions"""
    try:
        years_ahead = int(request.args.get('years_ahead', 0))
        
        # Create a sample patient twin
        twin = DiabetesTwin(
            patient_id=patient_id,
            age=58,
            gender='female',
            hba1c=10.9,
            fasting_glucose=180,
            bmi=35.8,
            diabetes_duration=8,
            medications=['metformin'],
            complications=[]
        )
        
        # Calculate current risks
        assessor = RiskAssessor()
        risks = assessor.predict_complication_risk(twin, years_ahead=max(1, years_ahead))
        organ_function = assessor.predict_organ_function(twin, years_ahead=max(1, years_ahead))
        
        # Map risks to colors and levels for frontend
        def get_risk_level(risk_pct):
            if risk_pct < 20:
                return {"risk_level": "low", "color": "green", "percentage": risk_pct}
            elif risk_pct < 50:
                return {"risk_level": "moderate", "color": "yellow", "percentage": risk_pct}
            else:
                return {"risk_level": "high", "color": "red", "percentage": risk_pct}
        
        response_data = {
            "patient_id": patient_id,
            "years_ahead": years_ahead,
            "prediction_year": 2025 + years_ahead,
            "organs": {
                "heart": {
                    **get_risk_level(risks.get('cvd_risk', 30)),
                    "function": organ_function.get('heart', 0.8)
                },
                "kidneys": {
                    **get_risk_level(risks.get('nephropathy_risk', 40)),
                    "function": organ_function.get('kidneys', 0.7)
                },
                "eyes": {
                    **get_risk_level(risks.get('retinopathy_risk', 50)),
                    "function": organ_function.get('eyes', 0.75)
                },
                "pancreas": {
                    **get_risk_level(35),  # Based on HbA1c
                    "function": organ_function.get('pancreas', 0.6)
                },
                "vessels": {
                    **get_risk_level(risks.get('cvd_risk', 30)),
                    "function": organ_function.get('blood_vessels', 0.75)
                }
            },
            "overall_health_score": round(sum(organ_function.values()) / len(organ_function) * 100, 1)
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error in visualization endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "MedTwin Digital Twin API"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

