"""
FastAPI Backend for MedTwin Digital Twin System
Provides REST API endpoints for patient twin operations
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db, Patient, AgentData
from digital_twin import DiabetesTwin
from simulation_engine import GlucoseSimulator, RiskAssessor

# --- AGENT INTEGRATION ---
import sys
import os

# Add GradProject to path to import agents
sys.path.append(os.path.join(os.path.dirname(__file__), "GradProject"))

try:
    from medtwin_agents import initialize_deepseek, AnalysisAgent, PlanningAgent, PredictionAgent, NotifierAgent
    
    # Initialize Agents (Try to get key from env, else use placeholder)
    # The user should set DEEPSEEK_API_KEY in their environment
    api_key = os.environ.get("DEEPSEEK_API_KEY") 
    print(f"DEBUG: Read API Name: '{api_key}'") # Debug print 
    if not api_key:
        print("⚠️  WARNING: DEEPSEEK_API_KEY not found. Agent features may fail or return mocks.")
        # fallback for demo if needed, or let it fail
    
    llm = initialize_deepseek(api_key)
    analysis_agent = AnalysisAgent(llm)
    planning_agent = PlanningAgent(llm)
    prediction_agent = PredictionAgent(llm)  # Added for organ-specific forecasting
    
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Agent Import Failed: {e}")
    AGENTS_AVAILABLE = False
except Exception as e:
    print(f"⚠️  Agent Initialization Failed: {e}")
    AGENTS_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(
    title="MedTwin API",
    description="Digital Twin API for Diabetes Type 2 Management",
    version="1.0.0"
)


# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MOUNT STATIC ASSETS
# Matches index.html's expectation of ./assets/...
if os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")
else:
    print("⚠️  'assets' directory not found. 3D models may fail to load.")

# MOUNT MODELS directory (Critical for 3D visualization)
if os.path.exists("models"):
    app.mount("/models", StaticFiles(directory="models"), name="models")
else:
    print("⚠️  'models' directory not found. 3D models will fail to load.")

# Database is now used instead of CSV
# df = pd.read_csv('diabetes_dataset.csv')
# twin_cache = {}


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class LifestyleChanges(BaseModel):
    """Model for lifestyle modification scenarios"""
    weight_loss_kg: Optional[float] = None
    exercise_level_change: Optional[str] = None
    calorie_reduction: Optional[int] = None
    quit_smoking: Optional[bool] = None
    reduce_alcohol: Optional[bool] = None


class SimulationRequest(BaseModel):
    """Request model for simulation endpoint"""
    patient_id: str
    lifestyle_changes: LifestyleChanges
    months: int = 6


class MealSimulationRequest(BaseModel):
    """Request model for meal simulation"""
    patient_id: str
    carbs_grams: float
    hours: int = 4


# ============================================================================
# HELPER FUNCTIONS
# ============================================================

def twin_to_qa_data(twin: DiabetesTwin) -> Dict:
    """Convert strict Twin structure to Agent's QA/Interview format with comprehensive data"""
    return {
        # Core Diabetes Metrics
        "What is your current HbA1c level?": f"{twin.metabolic_profile.hba1c_percent}%",
        "What is your fasting blood glucose?": f"{twin.metabolic_profile.fasting_glucose_mgdl} mg/dL",
        "Estimated Average Glucose": f"{twin.metabolic_profile.estimated_avg_glucose_mgdl:.0f} mg/dL",
        
        # Cardiovascular Markers
        "What are your blood pressure readings?": f"{twin.complications_status.bp_systolic}/{twin.complications_status.bp_diastolic} mmHg",
        "Total Cholesterol": f"{twin.complications_status.cholesterol_total} mg/dL",
        "LDL Cholesterol": f"{twin.complications_status.cholesterol_ldl} mg/dL",
        "HDL Cholesterol": f"{twin.complications_status.cholesterol_hdl} mg/dL",
        
        # Kidney/Liver Markers
        "GGT Level": f"{twin.complications_status.ggt} U/L",
        "Serum Urate": f"{twin.complications_status.serum_urate} mg/dL",
        
        # Lifestyle
        "Do you smoke?": twin.lifestyle.smoking_status,
        "How is your physical activity?": twin.lifestyle.physical_activity_level,
        "Alcohol consumption": twin.lifestyle.alcohol_consumption,
        "Daily caloric intake": f"{twin.lifestyle.dietary_intake_calories} kcal",
        
        # Demographics & Risk
        "What is your age?": str(twin.demographics.age),
        "What is your gender?": twin.demographics.gender,
        "BMI?": f"{twin.demographics.bmi:.1f}",
        "Waist circumference": f"{twin.demographics.waist_circumference_cm} cm",
        "Any family history of diabetes?": "Yes" if twin.risk_factors.family_history_diabetes else "No",
        
        # Current Risk Levels
        "Cardiovascular Risk": twin.complications_status.cardiovascular_risk.upper(),
        "Nephropathy Risk": twin.complications_status.nephropathy_risk.upper(),
        
        # Context
        "Condition": "Type 2 Diabetes Mellitus"
    }

def interpret_lab_value(name: str, value: float, unit: str = "") -> Dict:
    """
    Interpret a lab value and provide user-friendly explanation
    
    Args:
        name: Lab test name (e.g., "HbA1c", "LDL Cholesterol")
        value: Numeric value of the lab result
        unit: Unit of measurement (e.g., "%", "mg/dL")
    
    Returns:
        Dictionary with interpretation including status, target, and explanation
    """
    
    # Define lab value reference ranges and interpretations
    lab_standards = {
        "HbA1c": {
            "unit": "%",
            "normal_range": (4.0, 5.6),
            "diabetes_target": (0, 7.0),
            "ranges": [
                (0, 5.7, "EXCELLENT", "🟢", "Normal - no diabetes"),
                (5.7, 6.4, "PREDIABETES", "🟡", "Prediabetic range - lifestyle changes needed"),
                (6.5, 7.0, "CONTROLLED", "🟢", "Diabetes is well-controlled (at ADA target)"),
                (7.0, 8.0, "SUBOPTIMAL", "🟡", "Above target - medication adjustment may help"),
                (8.0, 9.0, "POOR", "🟠", "Poor control - need treatment intensification"),
                (9.0, 15.0, "CRITICAL", "🔴", "Very high - urgent intervention required")
            ]
        },
        "Fasting Glucose": {
            "unit": "mg/dL",
            "normal_range": (70, 100),
            "diabetes_target": (80, 130),
            "ranges": [
                (0, 70, "LOW", "🟡", "Risk of hypoglycemia - check with doctor"),
                (70, 100, "NORMAL", "🟢", "Normal fasting glucose"),
                (100, 125, "PREDIABETES", "🟡", "Elevated - prediabetic range"),
                (126, 180, "HIGH", "🟠", "Elevated - indicates poor diabetes control"),
                (180, 600, "VERY HIGH", "🔴", "Severely elevated - urgent attention needed")
            ]
        },
        "LDL Cholesterol": {
            "unit": "mg/dL",
            "normal_range": (0, 100),
            "diabetes_target": (0, 100),
            "ranges": [
                (0, 100, "OPTIMAL", "🟢", "Optimal for diabetes patients"),
                (100, 129, "NEAR OPTIMAL", "🟢", "Near optimal - acceptable for most"),
                (130, 159, "BORDERLINE HIGH", "🟡", "Consider statin therapy"),
                (160, 189, "HIGH", "🟠", "High - statin strongly recommended"),
                (190, 400, "VERY HIGH", "🔴", "Very high - aggressive lipid management needed")
            ]
        },
        "HDL Cholesterol": {
            "unit": "mg/dL",
            "normal_range": (40, 150),
            "diabetes_target": (40, 150),
            "ranges": [
                (0, 40, "LOW", "🟠", "Low HDL increases heart disease risk"),
                (40, 59, "ACCEPTABLE", "🟡", "Acceptable but could be higher"),
                (60, 150, "OPTIMAL", "🟢", "Optimal - protective against heart disease")
            ]
        },
        "Blood Pressure (Systolic)": {
            "unit": "mmHg",
            "normal_range": (90, 120),
            "diabetes_target": (0, 130),
            "ranges": [
                (0, 90, "LOW", "🟡", "Low blood pressure - monitor for dizziness"),
                (90, 120, "NORMAL", "🟢", "Normal blood pressure"),
                (120, 130, "ELEVATED", "🟡", "Elevated - lifestyle changes recommended"),
                (130, 140, "STAGE 1 HTN", "🟠", "Stage 1 hypertension - medication may be needed"),
                (140, 180, "STAGE 2 HTN", "🔴", "Stage 2 hypertension - medication required"),
                (180, 250, "CRISIS", "🔴", "Hypertensive crisis - seek immediate care")
            ]
        },
        "Total Cholesterol": {
            "unit": "mg/dL",
            "normal_range": (0, 200),
            "diabetes_target": (0, 200),
            "ranges": [
                (0, 200, "DESIRABLE", "🟢", "Desirable level"),
                (200, 239, "BORDERLINE HIGH", "🟡", "Borderline - lifestyle changes recommended"),
                (240, 500, "HIGH", "🔴", "High - medication likely needed")
            ]
        },
        "GGT": {
            "unit": "U/L",
            "normal_range": (0, 35),
            "diabetes_target": (0, 40),
            "ranges": [
                (0, 35, "NORMAL", "🟢", "Normal liver enzyme level"),
                (35, 50, "MILDLY ELEVATED", "🟡", "Mildly elevated - monitor kidney/liver function"),
                (50, 100, "ELEVATED", "🟠", "Elevated - may indicate kidney stress"),
                (100, 300, "HIGH", "🔴", "High - nephrology consultation recommended")
            ]
        },
        "Serum Urate": {
            "unit": "mg/dL",
            "normal_range": (3.5, 7.0),
            "diabetes_target": (0, 6.0),
            "ranges": [
                (0, 6.0, "NORMAL", "🟢", "Normal uric acid level"),
                (6.0, 7.0, "BORDERLINE", "🟡", "Borderline - monitor for kidney issues"),
                (7.0, 10.0, "HIGH", "🟠", "High - increases kidney disease risk"),
                (10.0, 20.0, "VERY HIGH", "🔴", "Very high - urgent kidney function assessment needed")
            ]
        },
        "BMI": {
            "unit": "kg/m²",
            "normal_range": (18.5, 24.9),
            "diabetes_target": (18.5, 24.9),
            "ranges": [
                (0, 18.5, "UNDERWEIGHT", "🟡", "Underweight - nutritional assessment needed"),
                (18.5, 24.9, "NORMAL", "🟢", "Normal weight"),
                (25.0, 29.9, "OVERWEIGHT", "🟡", "Overweight - 5-10% weight loss beneficial"),
                (30.0, 34.9, "OBESE CLASS I", "🟠", "Obesity - significant diabetes risk"),
                (35.0, 80.0, "OBESE CLASS II+", "🔴", "Severe obesity - intensive intervention needed")
            ]
        }
    }
    
    # Get lab standard or return basic interpretation if not defined
    if name not in lab_standards:
        return {
            "value": value,
            "unit": unit,
            "status": "UNKNOWN",
            "icon": "ℹ️",
            "explanation": f"Value: {value} {unit}"
        }
    
    lab = lab_standards[name]
    
    # Find which range the value falls into
    status = "UNKNOWN"
    icon = "ℹ️"
    explanation = ""
    
    for range_min, range_max, range_status, range_icon, range_explanation in lab["ranges"]:
        if range_min <= value < range_max:
            status = range_status
            icon = range_icon
            explanation = range_explanation
            break
    
    return {
        "value": value,
        "unit": lab["unit"],
        "status": status,
        "icon": icon,
        "normal_range": f"{lab['normal_range'][0]}-{lab['normal_range'][1]} {lab['unit']}",
        "diabetes_target": f"< {lab['diabetes_target'][1]} {lab['unit']}" if name in ["HbA1c", "LDL Cholesterol", "Blood Pressure (Systolic)"] else f"{lab['diabetes_target'][0]}-{lab['diabetes_target'][1]} {lab['unit']}",
        "explanation": explanation
    }


def get_or_create_twin(patient_id: str, db: Session) -> DiabetesTwin:
    """Get twin from database by loading latest agent data"""
    
    # 1. Check if patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found in database")
    
    # 2. Get latest medical data (Flexible JSON)
    # We look for the most recent data payload (could be from CSV import or updates)
    latest_record = db.query(AgentData)\
        .filter(AgentData.patient_id == patient_id)\
        .order_by(AgentData.timestamp.desc())\
        .first()
        
    if not latest_record:
        # Should not happen if migration ran
        raise HTTPException(status_code=404, detail="No medical records found for patient")
    
    # 3. Create Twin from JSON payload
    # logic: The payload structure matches exactly what df.iloc[i].to_dict() returned
    patient_data = latest_record.data_payload
    twin = DiabetesTwin(patient_id=patient_id, patient_data=patient_data)
    
    return twin


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Serve the 3D Dashboard"""
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "error", "message": "index.html not found"}


@app.get("/patients")
@app.get("/patients")
def list_patients(limit: int = 10, db: Session = Depends(get_db)):
    """Get list of available patients"""
    patients_list = []
    
    # Query patients
    db_patients = db.query(Patient).limit(limit).all()
    
    for p in db_patients:
        # Get latest data for this patient
        latest = db.query(AgentData)\
            .filter(AgentData.patient_id == p.id)\
            .order_by(AgentData.timestamp.desc())\
            .first()
            
        if latest and latest.data_payload:
            data = latest.data_payload
            patients_list.append({
                "patient_id": p.id,
                "age": int(data.get('Age', 0)),
                "gender": data.get('Sex', 'Unknown'),
                "hba1c": float(data.get('HbA1c', 0.0))
            })
    
    # Get total count
    total = db.query(Patient).count()
    
    return {
        "total_patients": total,
        "showing": len(patients_list),
        "patients": patients_list
    }


@app.get("/twin/{patient_id}")
def get_twin(patient_id: str, db: Session = Depends(get_db)):
    """
    Get complete digital twin for a patient
    
    Example: GET /twin/DM_00001
    """
    twin = get_or_create_twin(patient_id, db)
    return twin.to_dict()


@app.post("/twin/simulate")
def simulate_lifestyle_changes(request: SimulationRequest, db: Session = Depends(get_db)):
    """
    Simulate HbA1c changes based on lifestyle modifications
    
    Example:
    POST /twin/simulate
    {
        "patient_id": "DM_00001",
        "lifestyle_changes": {
            "weight_loss_kg": 10,
            "exercise_level_change": "Low_to_Moderate"
        },
        "months": 6
    }
    """
    twin = get_or_create_twin(request.patient_id, db)
    
    # Convert Pydantic model to dict, excluding None values
    changes = {k: v for k, v in request.lifestyle_changes.dict().items() if v is not None}
    
    predicted_hba1c, explanation = GlucoseSimulator.predict_hba1c_change(
        twin, changes, request.months
    )
    
    return {
        "patient_id": request.patient_id,
        "current_hba1c": twin.metabolic_profile.hba1c_percent,
        "predicted_hba1c": round(predicted_hba1c, 2),
        "change": round(predicted_hba1c - twin.metabolic_profile.hba1c_percent, 2),
        "months": request.months,
        "lifestyle_changes": changes,
        "explanation": explanation
    }


@app.post("/twin/meal-response")
def simulate_meal(request: MealSimulationRequest, db: Session = Depends(get_db)):
    """
    Simulate glucose response to a meal
    
    Example:
    POST /twin/meal-response
    {
        "patient_id": "DM_00001",
        "carbs_grams": 50,
        "hours": 4
    }
    """
    twin = get_or_create_twin(request.patient_id, db)
    
    # Calculate insulin resistance
    resistance = GlucoseSimulator.calculate_insulin_resistance(twin)
    
    # Simulate meal
    curve = GlucoseSimulator.simulate_meal_response(
        fasting_glucose=twin.metabolic_profile.fasting_glucose_mgdl,
        carbs_grams=request.carbs_grams,
        insulin_sensitivity=1/resistance,
        hours=request.hours
    )
    
    return {
        "patient_id": request.patient_id,
        "carbs_grams": request.carbs_grams,
        "insulin_resistance_factor": resistance,
        "fasting_glucose": twin.metabolic_profile.fasting_glucose_mgdl,
            "glucose_curve": curve
    }


@app.get("/twin/{patient_id}/risks")
def get_complication_risks(patient_id: str, years_ahead: int = 5, db: Session = Depends(get_db)):
    """
    Get long-term complication risk predictions
    
    Example: GET /twin/DM_00001/risks?years_ahead=5
    """
    twin = get_or_create_twin(patient_id, db)
    
    risks = RiskAssessor.predict_complication_risk(twin, years_ahead)
    
    return {
        "patient_id": patient_id,
        "years_ahead": years_ahead,
        "current_status": {
            "hba1c": twin.metabolic_profile.hba1c_percent,
            "cardiovascular_risk": twin.complications_status.cardiovascular_risk,
            "nephropathy_risk": twin.complications_status.nephropathy_risk
        },
        "predictions": risks
    }


@app.get("/twin/{patient_id}/visualization-data")
def get_visualization_data(patient_id: str, years_ahead: int = 0, db: Session = Depends(get_db)):
    """
    Get aggregated data specifically for the 3D Visualization frontend
    Updates predicted organ function based on years_ahead simulation
    """
    twin = get_or_create_twin(patient_id, db)
    base_hba1c = twin.metabolic_profile.hba1c_percent
    
    # Get organ function levels (personalized degradation)
    organ_functions = RiskAssessor.predict_organ_function(twin, years_ahead)
    
    # Get risk assessments
    risks = RiskAssessor.predict_complication_risk(twin, years_ahead=years_ahead)
    
    # Personalized HbA1c projection based on current control
    if years_ahead > 0:
        # Poor control = faster progression
        if base_hba1c >= 9.0:
            progression_rate = 0.25  # +0.25% per year
        elif base_hba1c >= 7.5:
            progression_rate = 0.15  # +0.15% per year  
        elif base_hba1c >= 6.5:
            progression_rate = 0.08  # +0.08% per year
        else:
            progression_rate = 0.05  # Minimal progression
        
        projected_hba1c = min(15.0, base_hba1c + (years_ahead * progression_rate))
    else:
        projected_hba1c = base_hba1c
    
    # Consistent color mapping function
    def get_risk_color(risk_level: str, function_level: float = None) -> str:
        """Map risk level and function to appropriate color for visualization"""
        if function_level is not None:
            if function_level < 0.4:
                return 'red'
            elif function_level < 0.7:
                return 'yellow'
            else:
                return 'green'
        # Fallback to risk level
        if risk_level == 'high':
            return 'red'
        elif risk_level == 'moderate':
            return 'yellow'
        else:
            return 'green'
    
    # Cognitive Analysis (Agent-Powered)
    cognitive_msg = "Cognitive Agent unavailable (Check API Key)"
    
    if AGENTS_AVAILABLE:
        try:
            if years_ahead > 0:
                # FUTURE SIMULATION: Construct comprehensive projected data for the agent
                sim_context = f"FUTURE SIMULATION: {years_ahead} YEARS FROM NOW (Year {2025 + years_ahead})"
                
                print(f"\n🧠 [DEBUG] Calling DeepSeek Agent for FUTURE prediction: Year {2025 + years_ahead}")
                print(f"   Projected HbA1c: {projected_hba1c:.1f}%, Pancreas: {organ_functions['pancreas']*100:.0f}%")
                
                # Build detailed future patient profile
                future_qa_data = {
                    # Projected values
                    "Projected HbA1c": f"{round(projected_hba1c, 1)}%",
                    "Projected Fasting Glucose": f"{int(twin.metabolic_profile.fasting_glucose_mgdl * (1 + years_ahead * 0.04))} mg/dL",
                    "Condition": "Type 2 Diabetes Mellitus - Unmanaged Progression",
                    
                    # Organ Function Status
                    "Pancreas Function": f"{int(organ_functions['pancreas'] * 100)}% (Beta-cell capacity)",
                    "Kidney Function": f"{int(organ_functions['kidneys'] * 100)}% (Estimated GFR proxy)",
                    "Heart Function": f"{int(organ_functions['heart'] * 100)}%",
                    "Eye Health": f"{int(organ_functions['eyes'] * 100)}% (Retinal integrity)",
                    "Nerve Function": f"{int(organ_functions['nerves'] * 100)}% (Peripheral sensation)",
                    
                    # Risk Scores
                    "Retinopathy Risk": f"{risks['retinopathy']['risk_level'].upper()} ({risks['retinopathy']['risk_score']}/100)",
                    "Nephropathy Risk": f"{risks['nephropathy']['risk_level'].upper()} ({risks['nephropathy']['risk_score']}/100)",
                    "Cardiovascular Risk": f"{risks['cardiovascular']['risk_level'].upper()} ({risks['cardiovascular']['risk_score']}/100)",
                    "Neuropathy Risk": f"{risks['neuropathy']['risk_level'].upper()} ({risks['neuropathy']['risk_score']}/100)",
                    
                    # Current patient context
                    "Patient Age": f"{twin.demographics.age + years_ahead} years (will be)",
                    "Current HbA1c": f"{base_hba1c}%",
                    "Blood Pressure": f"{twin.complications_status.bp_systolic}/{twin.complications_status.bp_diastolic} mmHg",
                    "BMI": f"{twin.demographics.bmi:.1f}",
                    "Smoking Status": twin.lifestyle.smoking_status,
                    "LDL Cholesterol": f"{twin.complications_status.cholesterol_ldl} mg/dL"
                }
                
                agent_input = {
                    "condition_type": "diabetes",
                    "qa_data": future_qa_data
                }
                
                # Invoke agent with simulation context
                analysis = analysis_agent.analyze(agent_input, simulation_context=sim_context)
                print(f"✅ [DEBUG] DeepSeek response received for Year {2025 + years_ahead}")
                cognitive_msg = f"🧠 COGNITIVE BRAIN ANALYSIS ({2025 + years_ahead}):\n{analysis.get('recommendations', 'Analysis failed')}"
            
            else:
                # CURRENT STATE ANALYSIS - Use comprehensive patient data with CALCULATED risk levels
                print(f"\n🧠 [DEBUG] Calling DeepSeek Agent for CURRENT state (Year 2025)")
                qa_data = twin_to_qa_data(twin)
                
                # Add calculated risk levels for consistency with visualization
                qa_data["Retinopathy Risk"] = f"{risks['retinopathy']['risk_level'].upper()} ({risks['retinopathy']['risk_score']}/100)"
                qa_data["Nephropathy Risk"] = f"{risks['nephropathy']['risk_level'].upper()} ({risks['nephropathy']['risk_score']}/100)"
                qa_data["Cardiovascular Risk"] = f"{risks['cardiovascular']['risk_level'].upper()} ({risks['cardiovascular']['risk_score']}/100)"
                qa_data["Neuropathy Risk"] = f"{risks['neuropathy']['risk_level'].upper()} ({risks['neuropathy']['risk_score']}/100)"
                
                agent_input = {
                    "condition_type": "diabetes",
                    "qa_data": qa_data
                }
                analysis = analysis_agent.analyze(agent_input)
                print(f"✅ [DEBUG] DeepSeek response received for current state")
                cognitive_msg = f"🧠 COGNITIVE BRAIN ANALYSIS:\n{analysis.get('recommendations', 'Analysis failed')}"

        except Exception as e:
            print(f"Agent Error: {e}")
            # FALLBACK: Use patient-specific dynamic messages
            if years_ahead > 0:
                highest_risk_organ = max(risks.items(), key=lambda x: x[1]['risk_score'])[0]
                risk_score = risks[highest_risk_organ]['risk_score']
                function_pct = int(organ_functions.get(highest_risk_organ.replace('cardiovascular', 'heart').replace('nephropathy', 'kidneys').replace('retinopathy', 'eyes'), 0.5) * 100)
                future_year = 2025 + years_ahead
                
                # Patient-specific fallback messages
                if highest_risk_organ == 'cardiovascular':
                    organ_name = 'Heart'
                    specific_msg = f"Cardiovascular risk score: {risk_score}/100. LDL: {twin.complications_status.cholesterol_ldl} mg/dL needs aggressive management."
                elif highest_risk_organ == 'nephropathy':
                    organ_name = 'Kidneys'
                    specific_msg = f"Nephropathy risk score: {risk_score}/100. GGT: {twin.complications_status.ggt} U/L. ACE inhibitor consideration warranted."
                elif highest_risk_organ == 'retinopathy':
                    organ_name = 'Eyes'
                    specific_msg = f"Retinopathy risk score: {risk_score}/100. BP: {twin.complications_status.bp_systolic}/{twin.complications_status.bp_diastolic} contributing to risk."
                elif highest_risk_organ == 'neuropathy':
                    organ_name = 'Nerves'
                    specific_msg = f"Neuropathy risk score: {risk_score}/100. Duration exposure and HbA1c of {projected_hba1c:.1f}% are primary drivers."
                else:
                    organ_name = highest_risk_organ.title()
                    specific_msg = f"Risk score: {risk_score}/100"
                
                cognitive_msg = (
                    f"⚠️ PROJECTION ({future_year}):\n"
                    f"Primary Concern: {organ_name} - Function at {function_pct}%\n"
                    f"{specific_msg}\n\n"
                    f"• HbA1c: {base_hba1c}% → {projected_hba1c:.1f}% (+{projected_hba1c - base_hba1c:.1f}%)\n"
                    f"• Pancreas Function: {int(organ_functions['pancreas'] * 100)}%\n"
                    f"• Overall Control: {'POOR' if projected_hba1c >= 9 else 'FAIR' if projected_hba1c >= 7 else 'GOOD'}"
                )
            else:
                # Current state fallback
                control_status = "POOR" if base_hba1c >= 9 else "FAIR" if base_hba1c >= 7 else "GOOD"
                highest_risk = max(risks.items(), key=lambda x: x[1]['risk_score'])
                
                cognitive_msg = (
                    f"📊 CURRENT ASSESSMENT:\n"
                    f"Glycemic Control: {control_status} (HbA1c: {base_hba1c}%)\n"
                    f"Fasting Glucose: {twin.metabolic_profile.fasting_glucose_mgdl} mg/dL\n"
                    f"Highest Risk: {highest_risk[0].title()} ({highest_risk[1]['risk_level'].upper()})\n\n"
                    f"Key Metrics:\n"
                    f"• BP: {twin.complications_status.bp_systolic}/{twin.complications_status.bp_diastolic} mmHg\n"
                    f"• LDL: {twin.complications_status.cholesterol_ldl} mg/dL\n"
                    f"• BMI: {twin.demographics.bmi:.1f}"
                )
    else:
        # Fallback if agents didn't even import
        cognitive_msg = (
            f"Cognitive System Offline.\n"
            f"Patient HbA1c: {base_hba1c}% | Projected: {projected_hba1c:.1f}%"
        )
    
    # Add AI-powered organ predictions if PredictionAgent is available
    ai_predictions = {}
    if AGENTS_AVAILABLE:
        try:
            # Get comprehensive organ impact prediction from PredictionAgent
            organ_prediction = prediction_agent.predict_organ_impact('diabetes', qa_data)
            progression_prediction = prediction_agent.predict_progression(
                'diabetes', 
                qa_data, 
                current_severity='HIGH' if base_hba1c >= 9 else 'MODERATE' if base_hba1c >= 7 else 'LOW'
            )
            
            ai_predictions = {
                "organ_impact": organ_prediction,
                "progression": progression_prediction
            }
            print(f"✅ [DEBUG] PredictionAgent generated organ-specific forecasts")
        except Exception as e:
            print(f"⚠️ PredictionAgent Error: {e}")
            ai_predictions = {
                "organ_impact": {"affected_organs": [], "systemic_risks": "Prediction unavailable"},
                "progression": {"worsening": False, "progression_forecast": "Unable to predict", "risk_factors": []}
            }

    return {
        "patient_id": patient_id,
        "years_ahead": years_ahead,
        "projected_hba1c": round(projected_hba1c, 1),
        "organs": {
            "pancreas": {
                "risk_level": "high" if organ_functions['pancreas'] < 0.4 else "moderate" if organ_functions['pancreas'] < 0.7 else "low",
                "function_level": organ_functions['pancreas'],
                "color": get_risk_color("", organ_functions['pancreas']),
                "status": "exhausted" if organ_functions['pancreas'] < 0.3 else "impaired" if organ_functions['pancreas'] < 0.6 else "functioning",
                "hba1c": round(projected_hba1c, 1)
            },
            "vessels": {
                "risk_level": "high" if organ_functions['vessels'] < 0.4 else "moderate" if organ_functions['vessels'] < 0.7 else "low",
                "glycation_level": round(1 - organ_functions['vessels'], 2),
                "function_level": organ_functions['vessels'],
                "color": get_risk_color("", organ_functions['vessels']),
                "status": "crystallized" if organ_functions['vessels'] < 0.4 else "damaged" if organ_functions['vessels'] < 0.7 else "healthy",
                "avg_glucose": twin.metabolic_profile.estimated_avg_glucose_mgdl
            },
            "kidneys": {
                "risk_level": risks['nephropathy']['risk_level'],
                "function_level": organ_functions['kidneys'],
                "color": get_risk_color(risks['nephropathy']['risk_level']),  # Use ONLY risk_level for color
                "future_risk_score": risks['nephropathy']['risk_score'],
                "recommendation": risks['nephropathy']['recommendation']
            },
            "eyes": {
                "risk_level": risks['retinopathy']['risk_level'],
                "function_level": organ_functions['eyes'],
                "color": get_risk_color(risks['retinopathy']['risk_level']),  # Use ONLY risk_level for color
                "risk_score": risks['retinopathy']['risk_score'],
                "recommendation": risks['retinopathy']['recommendation']
            },
            "heart": {
                "risk_level": risks['cardiovascular']['risk_level'],
                "function_level": organ_functions['heart'],
                "color": get_risk_color(risks['cardiovascular']['risk_level']),  # Use ONLY risk_level for color
                "future_risk_score": risks['cardiovascular']['risk_score'],
                "recommendation": risks['cardiovascular']['recommendation']
            }
        },
        "summary": {
            "overall_control": "good" if projected_hba1c < 7 else "fair" if projected_hba1c < 9 else "poor",
            "highest_risk_organ": max(risks.items(), key=lambda x: x[1]['risk_score'])[0],
            "cognitive_prediction": cognitive_msg
        },
        "ai_predictions": ai_predictions,  # Added: Organ-specific AI forecasts from PredictionAgent
        "lab_interpretations": {  # NEW: User-friendly lab value explanations
            "hba1c": interpret_lab_value("HbA1c", twin.metabolic_profile.hba1c_percent),
            "fasting_glucose": interpret_lab_value("Fasting Glucose", twin.metabolic_profile.fasting_glucose_mgdl),
            "ldl_cholesterol": interpret_lab_value("LDL Cholesterol", twin.complications_status.cholesterol_ldl),
            "hdl_cholesterol": interpret_lab_value("HDL Cholesterol", twin.complications_status.cholesterol_hdl),
            "total_cholesterol": interpret_lab_value("Total Cholesterol", twin.complications_status.cholesterol_total),
            "blood_pressure": interpret_lab_value("Blood Pressure (Systolic)", twin.complications_status.bp_systolic),
            "ggt": interpret_lab_value("GGT", twin.complications_status.ggt),
            "serum_urate": interpret_lab_value("Serum Urate", twin.complications_status.serum_urate),
            "bmi": interpret_lab_value("BMI", twin.demographics.bmi)
        }
    }


@app.get("/twin/{patient_id}/action-plan")
def get_action_plan(patient_id: str, db: Session = Depends(get_db)):
    """
    Generate actionable treatment plan using PlanningAgent
    """
    twin = get_or_create_twin(patient_id, db)
    
    if not AGENTS_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "AI Agents not initialized. Action planning requires DeepSeek API.",
            "fallback_plan": {
                "short_term": ["Monitor blood glucose daily", "Take prescribed medications", "Track diet"],
                "long_term": ["Schedule 3-month HbA1c recheck", "Aim for HbA1c < 7%"]
            }
        }
    
    try:
        # Prepare data for analysis
        qa_data = twin_to_qa_data(twin)
        
        # Get risk assessments
        risks = RiskAssessor.predict_complication_risk(twin, years_ahead=0)
        
        # Get analysis from AnalysisAgent first
        analysis_result = analysis_agent.analyze({"condition_type": "diabetes", "qa_data": qa_data})
        
        # Create comprehensive plan using PlanningAgent
        treatment_plan = planning_agent.create_comprehensive_plan(analysis_result)
        
        return {
            "status": "success",
            "patient_id": patient_id,
            "condition": "diabetes",
            "severity": "MODERATE", # You could calculate this dynamically
            "short_term_plan": treatment_plan.get("short_term_plan", {}),
            "long_term_plan": treatment_plan.get("long_term_plan", {}),
            "created_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"❌ PlanningAgent Error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "fallback_plan": {
                "short_term": [
                    "Monitor blood glucose twice daily",
                    "Take prescribed medications as scheduled",
                    "Track carbohydrate intake",
                    "Check blood pressure weekly"
                ],
                "long_term": [
                    "Schedule comprehensive diabetes exam in 3 months",
                    "Target HbA1c < 7.0%",
                    "Aim for 5-10% body weight reduction if overweight"
                ]
            }
        }


class AgentDataInput(BaseModel):
    agent_type: str
    data_payload: Dict

@app.post("/twin/{patient_id}/add-data")
def add_flexible_data(patient_id: str, input_data: AgentDataInput, db: Session = Depends(get_db)):
    """
    Store ANY data from ANY agent efficiently.
    This uses the Flexible JSON Schema.
    
    Example:
    POST /twin/DM_00001/add-data
    {
        "agent_type": "DietaryLog",
        "data_payload": {"calories": 2500, "carbs": 300, "mood": "Happy"}
    }
    """
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
         raise HTTPException(status_code=404, detail="Patient not found")
         
    # Create new record
    new_record = AgentData(
        patient_id=patient_id,
        agent_type=input_data.agent_type,
        data_payload=input_data.data_payload,
        timestamp=datetime.utcnow()
    )
    
    db.add(new_record)
    db.commit()
    
    return {"status": "success", "message": f"Added records for {input_data.agent_type}"}



class MedicationInput(BaseModel):
    drugs: List[str]

@app.post("/twin/{patient_id}/simulate-medication")
def simulate_medication(patient_id: str, input_data: MedicationInput, db: Session = Depends(get_db)):
    """
    Simulate the effect of medications ("What-If" Scenario).
    Returns predicted HbA1c AND prevented risks.
    """
    from simulation_engine import MedicationSimulator, RiskAssessor
    
    twin = get_or_create_twin(patient_id, db)
    current_hba1c = twin.metabolic_profile.hba1c_percent
    
    # 1. Simulate Drug Effect (HbA1c Drop)
    simulation_result = MedicationSimulator.simulate_treatment(
        current_hba1c=current_hba1c,
        drugs=input_data.drugs
    )
    
    new_hba1c = simulation_result['predicted_hba1c']
    
    # 2. Simulate Risk Reduction
    # Create a "Future Twin" with the new health stats
    # We use data manipulation to clone parameters temporarily
    import copy
    future_twin = copy.deepcopy(twin)
    future_twin.metabolic_profile.hba1c_percent = new_hba1c
    
    # Check weight impact
    if simulation_result['weight_impact_kg'] != 0:
        # Adjustment for BMI specific logic if needed
        pass 

    # Calculate Risks for BOTH scenarios (Current vs Treated)
    current_risks = RiskAssessor.predict_complication_risk(twin, years_ahead=5)
    treated_risks = RiskAssessor.predict_complication_risk(future_twin, years_ahead=5)
    
    # Compare
    risk_comparison = {}
    for organ, data in current_risks.items():
        old_score = data['risk_score']
        new_score = treated_risks[organ]['risk_score']
        reduction = old_score - new_score
        
        if reduction > 0:
            risk_comparison[organ] = {
                "before": old_score,
                "after": new_score,
                "improvement": f"{reduction} points lower risk",
                "status": "IMPROVED"
            }
        else:
            risk_comparison[organ] = {
                "before": old_score,
                "after": new_score,
                "status": "UNCHANGED"
            }

    return {
        "status": "success",
        "patient_id": patient_id,
        "input_drugs": input_data.drugs,
        "metabolic_impact": simulation_result,
        "clinical_outcome": {
            "risk_reduction_5yr": risk_comparison,
            "summary": f"Treatment reduces HbA1c by {simulation_result['hba1c_reduction']}% and improves long-term outcomes."
        }
    }

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("="*70)
    print("🚀 Starting MedTwin API Server")
    print("="*70)
    print("\n📍 API will be available at: http://localhost:8000")
    print("📖 Interactive docs at: http://localhost:8000/docs")
    print("\n🔗 Example endpoints:")
    print("   GET  http://localhost:8000/twin/DM_00001")
    print("   POST http://localhost:8000/twin/simulate")
    print("   GET  http://localhost:8000/twin/DM_00001/visualization-data")
    print("   GET  http://localhost:8000/twin/DM_00001/action-plan  (NEW: Treatment plans)")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
