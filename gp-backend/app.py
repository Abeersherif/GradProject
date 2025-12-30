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
CORS(app, resources={
    r"/*": {
        "origins": [
            FRONTEND_URL,
            "https://medtwinweb.onrender.com",
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
        
        # Create a mock patient dictionary for the simulation engine
        # In production, this would come from a database query using patient_id
        mock_patient_data = {
            "Age": 58,
            "Sex": "Female",
            "Ethnicity": "Middle Eastern",
            "BMI": 35.8,
            "Waist_Circumference": 105.0,
            "HbA1c": 10.9,
            "Fasting_Blood_Glucose": 180.0,
            "Blood_Pressure_Systolic": 145,
            "Blood_Pressure_Diastolic": 92,
            "Cholesterol_Total": 220.0,
            "Cholesterol_HDL": 40.0,
            "Cholesterol_LDL": 160.0,
            "GGT": 45.0,
            "Serum_Urate": 6.8,
            "Physical_Activity_Level": "Low",
            "Dietary_Intake_Calories": 2400,
            "Alcohol_Consumption": "None",
            "Smoking_Status": "Never",
            "Family_History_of_Diabetes": 1,
            "Previous_Gestational_Diabetes": 0
        }
        
        # Correctly initialize the twin using a dictionary as required by the class
        twin = DiabetesTwin(
            patient_id=f"DM_{patient_id:05d}",
            patient_data=mock_patient_data
        )
        
        # Calculate risks using the prediction engine
        assessor = RiskAssessor()
        risks = assessor.predict_complication_risk(twin, years_ahead=max(1, years_ahead))
        organ_function = assessor.predict_organ_function(twin, years_ahead=max(1, years_ahead))
        
        # Map percentages and risk levels to colors for the 3D frontend
        def get_risk_level(risk_pct):
            if risk_pct < 20:
                return {"risk_level": "low", "color": "green", "percentage": risk_pct}
            elif risk_pct < 50:
                return {"risk_level": "moderate", "color": "yellow", "percentage": risk_pct}
            else:
                return {"risk_level": "high", "color": "red", "percentage": risk_pct}
        
        # Consolidate results for original organs
        response_data = {
            "patient_id": patient_id,
            "years_ahead": years_ahead,
            "prediction_year": 2025 + years_ahead,
            "organs": {
                "heart": {
                    **get_risk_level(risks.get('cvd_risk', 30)),
                    "function": round(organ_function.get('heart', 0.8), 2)
                },
                "kidneys": {
                    **get_risk_level(risks.get('nephropathy_risk', 40)),
                    "function": round(organ_function.get('kidneys', 0.7), 2)
                },
                "eyes": {
                    **get_risk_level(risks.get('retinopathy_risk', 50)),
                    "function": round(organ_function.get('eyes', 0.75), 2)
                },
                "pancreas": {
                    **get_risk_level(35 + (years_ahead * 2)),  # Pancreas degrades over time
                    "function": round(organ_function.get('pancreas', 0.6), 2)
                },
                "vessels": {
                    **get_risk_level(risks.get('cvd_risk', 30)),
                    "function": round(organ_function.get('blood_vessels', 0.75), 2)
                }
            },
            "overall_health_score": round(sum(organ_function.values()) / len(organ_function) * 100, 1)
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error in visualization endpoint: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "MedTwin Digital Twin API"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

