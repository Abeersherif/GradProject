from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from digital_twin import DiabetesTwin
from simulation_engine import GlucoseSimulator, RiskAssessor
from werkzeug.security import check_password_hash
from datetime import datetime
import os
import json
import logging
import sqlite3

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

# --- DATABASE HELPER ---

def get_db_connection():
    # Look for database in various locations
    db_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'instance', 'medtwin.db'),
        os.path.join(os.path.dirname(__file__), 'instance', 'medtwin.db'),
        os.path.join(os.getcwd(), 'instance', 'medtwin.db'),
        'instance/medtwin.db'
    ]
    
    for path in db_paths:
        if os.path.exists(path):
            logger.info(f"Using database at: {path}")
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
            return conn
            
    logger.warning("Database not found, using mocks")
    return None

def calculate_age(dob_str):
    if not dob_str:
        return 58  # Default demo age
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d')
        today = datetime.now()
        return today.year - dob.year - ((today.month, today.day) < (today.month, today.day))
    except:
        return 58

# --- AUTH ROUTES ---

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    logger.info(f"Login attempt for: {email}")
    
    # Try real database first
    conn = get_db_connection()
    if conn:
        try:
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            if user:
                # Store user as dict for easier handling
                user_dict = dict(user)
                # Password check (demo-friendly: allow if matches or if it's the specific test user we saw)
                # In production, check_password_hash is mandatory
                password_correct = False
                if user_dict.get('password_hash'):
                    try:
                        password_correct = check_password_hash(user_dict['password_hash'], password)
                    except:
                        # Fallback for manual testing/migration issues
                        password_correct = (password == "Password123")
                else:
                    password_correct = (password == "Password123")

                if password_correct or password == "Abeer123": # Debug backdoor for developer
                    logger.info(f"✅ Real user login successful: {email}")
                    return jsonify({
                        "access_token": "real-token-v1",
                        "user": {
                            "id": user_dict['id'],
                            "email": user_dict['email'],
                            "name": user_dict['full_name'],
                            "sex": user_dict.get('gender', 'Female'),
                            "role": user_dict['role']
                        }
                    }), 200
        except Exception as e:
            logger.error(f"Database error during login: {e}")
        finally:
            conn.close()

    # Demo fallback for "abeersheri" or non-existent in DB
    if email == "abeersheri@demo.com" or email == "abeersheri":
        return jsonify({
            "access_token": "mock-token-123",
            "user": {
                "id": 1,
                "email": email,
                "name": "Abeer Sherif",
                "sex": "Female",
                "role": "patient"
            }
        }), 200
        
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/auth/register/patient', methods=['POST'])
def register_patient():
    data = request.json
    return jsonify({
        "access_token": "mock-token-reg",
        "user": {
            "id": 1,
            "email": data.get('email'),
            "name": data.get('name', 'New Patient'),
            "sex": data.get('sex', 'Female'),  # Get from signup form
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
        
        # Default mock data in case DB fetch fails
        patient_profile = {
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

        # Fetch REAL data from database
        conn = get_db_connection()
        if conn:
            try:
                user = conn.execute('SELECT * FROM users WHERE id = ?', (patient_id,)).fetchone()
                if user:
                    u = dict(user)
                    logger.info(f"✅ Fetched real data for patient {patient_id}")
                    
                    # Map database fields to simulation engine fields
                    real_metrics = {
                        "Age": calculate_age(u.get('dob')),
                        "Sex": u.get('gender', 'Female'),
                        "HbA1c": u.get('hba1c', 10.9) or 10.9,
                        "Fasting_Blood_Glucose": u.get('last_glucose', 180.0) or 180.0,
                    }
                    
                    # Calculate BMI if weight/height available
                    if u.get('weight') and u.get('height') and u['height'] > 0:
                        height_m = u['height'] / 100 if u['height'] > 10 else u['height'] # Handle cm vs m
                        real_metrics["BMI"] = round(u['weight'] / (height_m ** 2), 1)
                    
                    # Update patient profile with real data
                    patient_profile.update(real_metrics)
                    logger.info(f"Updated profile: Name={u['full_name']}, Age={patient_profile['Age']}, Gender={patient_profile['Sex']}")
            except Exception as e:
                logger.error(f"Error fetching patient from DB: {e}")
            finally:
                conn.close()
        
        # Initialize the twin using the consolidated data
        twin = DiabetesTwin(
            patient_id=f"DM_{patient_id:05d}",
            patient_data=patient_profile
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

