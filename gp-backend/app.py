from flask import Flask, jsonify, request
from flask_cors import CORS
from digital_twin import DiabetesTwin
from simulation_engine import GlucoseSimulator, RiskAssessor
import os

app = Flask(__name__)

# Get frontend URL from environment variable for production
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

# CORS configuration - Allow frontend to access backend
CORS(app, resources={
    r"/api/*": {
        "origins": [
            FRONTEND_URL,
            "https://medtwinweb.onrender.com",
            "http://localhost:5173",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route('/api/twin/<int:patient_id>/visualization-data', methods=['GET'])
def get_visualization_data(patient_id):
    """Get organ visualization data with risk levels for future predictions"""
    try:
        years_ahead = int(request.args.get('years_ahead', 0))
        
        # Create a sample patient twin (in production, load from database)
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
        print(f"Error in visualization endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "MedTwin Digital Twin API"}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
