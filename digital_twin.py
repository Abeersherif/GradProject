"""
Digital Twin Core - Patient Twin Class
This is the heart of your MedTwin system for Diabetes Type 2
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime
import json


@dataclass
class Demographics:
    """Patient demographic information"""
    age: int
    gender: str
    ethnicity: str
    bmi: float
    waist_circumference_cm: float


@dataclass
class MetabolicProfile:
    """Core diabetes metabolic markers"""
    hba1c_percent: float
    fasting_glucose_mgdl: float
    estimated_avg_glucose_mgdl: float  # Calculated from HbA1c
    
    def __post_init__(self):
        """Auto-calculate average glucose from HbA1c"""
        if self.estimated_avg_glucose_mgdl is None:
            self.estimated_avg_glucose_mgdl = (self.hba1c_percent * 28.7) - 46.7


@dataclass
class ComplicationsStatus:
    """Diabetes complication risk indicators"""
    cardiovascular_risk: str  # "low", "moderate", "high"
    nephropathy_risk: str     # "low", "moderate", "high"
    bp_systolic: int
    bp_diastolic: int
    cholesterol_total: float
    cholesterol_hdl: float
    cholesterol_ldl: float
    ggt: float  # Liver enzyme - kidney risk indicator
    serum_urate: float


@dataclass
class LifestyleFactors:
    """Patient lifestyle and behavior"""
    physical_activity_level: str  # "Low", "Moderate", "High"
    dietary_intake_calories: int
    alcohol_consumption: str  # "None", "Moderate", "Heavy"
    smoking_status: str  # "Never", "Former", "Current"


@dataclass
class RiskFactors:
    """Genetic and historical risk factors"""
    family_history_diabetes: bool
    previous_gestational_diabetes: bool


@dataclass
class OrganHealth:
    """
    Organ health status for visualization and simulation.
    Values are 0.0 (complete failure) to 1.0 (perfect health).
    """
    pancreas: float = 1.0  # Beta-cell function
    kidneys: float = 1.0   # GFR proxy
    heart: float = 1.0     # Cardiovascular health
    eyes: float = 1.0      # Retinal integrity
    vessels: float = 1.0   # Vascular health
    nerves: float = 1.0    # Peripheral nerve function
    
    def get_lowest(self) -> tuple:
        """Return the organ with lowest function"""
        organs = {
            'pancreas': self.pancreas,
            'kidneys': self.kidneys,
            'heart': self.heart,
            'eyes': self.eyes,
            'vessels': self.vessels,
            'nerves': self.nerves
        }
        lowest = min(organs.items(), key=lambda x: x[1])
        return lowest  # (name, value)


@dataclass 
class Medication:
    """Single medication entry"""
    name: str
    dosage: str
    frequency: str  # e.g., "once daily", "twice daily"
    category: str   # e.g., "diabetes", "blood_pressure", "cholesterol"
    start_date: str = ""
    active: bool = True


@dataclass
class MedicationHistory:
    """Patient's medication history for treatment simulation"""
    current_medications: list = None  # List of Medication objects
    
    def __post_init__(self):
        if self.current_medications is None:
            self.current_medications = []
    
    def add_medication(self, med: Medication):
        self.current_medications.append(med)
    
    def get_diabetes_meds(self) -> list:
        return [m for m in self.current_medications if m.category == "diabetes" and m.active]
    
    def get_bp_meds(self) -> list:
        return [m for m in self.current_medications if m.category == "blood_pressure" and m.active]
    
    def is_on_medication(self, category: str) -> bool:
        return any(m.category == category and m.active for m in self.current_medications)


class DiabetesTwin:
    """
    Digital Twin for a Diabetes Type 2 Patient
    
    This class represents the virtual replica of a patient,
    containing all their health data and prediction capabilities.
    """
    
    def __init__(self, patient_id: str, patient_data: Dict):
        """
        Initialize a Digital Twin from patient data
        
        Args:
            patient_id: Unique identifier (e.g., "DM_00001")
            patient_data: Dictionary containing patient information
        """
        self.patient_id = patient_id
        self.created_at = datetime.now().isoformat()
        self.last_updated = self.created_at
        
        # Build the twin components
        self.demographics = Demographics(
            age=int(patient_data['Age']),
            gender=patient_data['Sex'],
            ethnicity=patient_data['Ethnicity'],
            bmi=float(patient_data['BMI']),
            waist_circumference_cm=float(patient_data['Waist_Circumference'])
        )
        
        self.metabolic_profile = MetabolicProfile(
            hba1c_percent=float(patient_data['HbA1c']),
            fasting_glucose_mgdl=float(patient_data['Fasting_Blood_Glucose']),
            estimated_avg_glucose_mgdl=None  # Will be auto-calculated
        )
        
        self.complications_status = ComplicationsStatus(
            cardiovascular_risk=self._calculate_cv_risk(patient_data),
            nephropathy_risk=self._calculate_nephropathy_risk(patient_data),
            bp_systolic=int(patient_data['Blood_Pressure_Systolic']),
            bp_diastolic=int(patient_data['Blood_Pressure_Diastolic']),
            cholesterol_total=float(patient_data['Cholesterol_Total']),
            cholesterol_hdl=float(patient_data['Cholesterol_HDL']),
            cholesterol_ldl=float(patient_data['Cholesterol_LDL']),
            ggt=float(patient_data['GGT']),
            serum_urate=float(patient_data['Serum_Urate'])
        )
        
        self.lifestyle = LifestyleFactors(
            physical_activity_level=patient_data['Physical_Activity_Level'],
            dietary_intake_calories=int(patient_data['Dietary_Intake_Calories']),
            alcohol_consumption=patient_data['Alcohol_Consumption'],
            smoking_status=patient_data['Smoking_Status']
        )
        
        self.risk_factors = RiskFactors(
            family_history_diabetes=bool(patient_data['Family_History_of_Diabetes']),
            previous_gestational_diabetes=bool(patient_data['Previous_Gestational_Diabetes'])
        )
        
        # Initialize organ health based on current metabolic state
        self.organ_health = self._initialize_organ_health(patient_data)
        
        # Initialize empty medication history (can be populated later)
        self.medications = MedicationHistory()
    
    def _initialize_organ_health(self, data: Dict) -> OrganHealth:
        """Calculate initial organ health based on patient data"""
        # Start at 100% and degrade based on risk factors
        hba1c = float(data['HbA1c'])
        bp = int(data['Blood_Pressure_Systolic'])
        
        # Pancreas: Degrades with poor glycemic control
        pancreas = max(0.3, 1.0 - (hba1c - 5.0) * 0.08)
        
        # Kidneys: Affected by BP and HbA1c
        kidneys = max(0.4, 1.0 - (bp - 120) * 0.005 - (hba1c - 6) * 0.05)
        
        # Heart: CV risk factors
        heart = max(0.5, 1.0 - (hba1c - 6) * 0.03 - (bp - 120) * 0.003)
        if data.get('Smoking_Status') == 'Current':
            heart -= 0.1
        
        # Eyes: Retinopathy risk based on HbA1c
        eyes = max(0.4, 1.0 - (hba1c - 5.5) * 0.06)
        
        # Vessels: LDL and BP
        ldl = float(data.get('Cholesterol_LDL', 100))
        vessels = max(0.4, 1.0 - (ldl - 100) * 0.003 - (bp - 120) * 0.003)
        
        # Nerves: HbA1c and duration (assume based on severity)
        nerves = max(0.5, 1.0 - (hba1c - 5.5) * 0.05)
        
        return OrganHealth(
            pancreas=round(pancreas, 2),
            kidneys=round(kidneys, 2),
            heart=round(heart, 2),
            eyes=round(eyes, 2),
            vessels=round(vessels, 2),
            nerves=round(nerves, 2)
        )
    
    def _calculate_cv_risk(self, data: Dict) -> str:
        """Calculate cardiovascular risk level"""
        risk_score = 0
        
        # Age risk
        if data['Age'] > 60:
            risk_score += 2
        elif data['Age'] > 45:
            risk_score += 1
        
        # Blood pressure risk
        if data['Blood_Pressure_Systolic'] >= 140:
            risk_score += 2
        elif data['Blood_Pressure_Systolic'] >= 130:
            risk_score += 1
        
        # Cholesterol risk
        if data['Cholesterol_LDL'] >= 160:
            risk_score += 2
        elif data['Cholesterol_LDL'] >= 130:
            risk_score += 1
        
        # Smoking
        if data['Smoking_Status'] == 'Current':
            risk_score += 2
        
        # HbA1c (poor control increases CV risk)
        if data['HbA1c'] >= 9.0:
            risk_score += 2
        elif data['HbA1c'] >= 7.5:
            risk_score += 1
        
        # Classify
        if risk_score >= 6:
            return "high"
        elif risk_score >= 3:
            return "moderate"
        else:
            return "low"
    
    def _calculate_nephropathy_risk(self, data: Dict) -> str:
        """Calculate kidney disease risk level"""
        risk_score = 0
        
        # GGT (liver enzyme, but correlates with kidney issues)
        if data['GGT'] >= 60:
            risk_score += 2
        elif data['GGT'] >= 40:
            risk_score += 1
        
        # Serum Urate (uric acid)
        if data['Serum_Urate'] >= 7.0:
            risk_score += 2
        elif data['Serum_Urate'] >= 6.0:
            risk_score += 1
        
        # Blood pressure
        if data['Blood_Pressure_Systolic'] >= 140:
            risk_score += 1
        
        # HbA1c
        if data['HbA1c'] >= 8.0:
            risk_score += 2
        elif data['HbA1c'] >= 7.0:
            risk_score += 1
        
        # Classify
        if risk_score >= 5:
            return "high"
        elif risk_score >= 3:
            return "moderate"
        else:
            return "low"
    
    def to_dict(self) -> Dict:
        """Convert the twin to a dictionary (for JSON export)"""
        return {
            "patient_id": self.patient_id,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "demographics": asdict(self.demographics),
            "metabolic_profile": asdict(self.metabolic_profile),
            "complications_status": asdict(self.complications_status),
            "lifestyle": asdict(self.lifestyle),
            "risk_factors": asdict(self.risk_factors),
            "organ_health": asdict(self.organ_health),
            "medications": [asdict(m) for m in self.medications.current_medications]
        }
    
    def to_json(self, indent=2) -> str:
        """Export twin as JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the patient"""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║  DIGITAL TWIN SUMMARY - {self.patient_id}
╚══════════════════════════════════════════════════════════════╝

👤 DEMOGRAPHICS
   Age: {self.demographics.age} years
   Gender: {self.demographics.gender}
   BMI: {self.demographics.bmi:.1f} kg/m²
   Waist: {self.demographics.waist_circumference_cm:.1f} cm

🩺 METABOLIC STATUS
   HbA1c: {self.metabolic_profile.hba1c_percent:.1f}% {'🔴 HIGH' if self.metabolic_profile.hba1c_percent >= 7.0 else '🟢 CONTROLLED'}
   Fasting Glucose: {self.metabolic_profile.fasting_glucose_mgdl:.0f} mg/dL
   Est. Avg Glucose: {self.metabolic_profile.estimated_avg_glucose_mgdl:.0f} mg/dL

⚠️  COMPLICATION RISKS
   Cardiovascular: {self.complications_status.cardiovascular_risk.upper()}
   Kidney Disease: {self.complications_status.nephropathy_risk.upper()}
   Blood Pressure: {self.complications_status.bp_systolic}/{self.complications_status.bp_diastolic} mmHg

🏃 LIFESTYLE
   Activity Level: {self.lifestyle.physical_activity_level}
   Daily Calories: {self.lifestyle.dietary_intake_calories} kcal
   Smoking: {self.lifestyle.smoking_status}
   Alcohol: {self.lifestyle.alcohol_consumption}

🧬 RISK FACTORS
   Family History: {'Yes' if self.risk_factors.family_history_diabetes else 'No'}
   Gestational Diabetes: {'Yes' if self.risk_factors.previous_gestational_diabetes else 'No'}
"""
    
    def __repr__(self):
        return f"DiabetesTwin(patient_id='{self.patient_id}', HbA1c={self.metabolic_profile.hba1c_percent:.1f}%)"


# Example usage
if __name__ == "__main__":
    # Load a sample patient from the dataset
    import pandas as pd
    
    df = pd.read_csv('diabetes_dataset.csv')
    
    # Create a twin for the first patient
    sample_patient = df.iloc[0].to_dict()
    twin = DiabetesTwin(patient_id="DM_00001", patient_data=sample_patient)
    
    # Display the twin
    print(twin.get_summary())
    
    # Export as JSON
    print("\n" + "="*60)
    print("JSON EXPORT:")
    print("="*60)
    print(twin.to_json())
