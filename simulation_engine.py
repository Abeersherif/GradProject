"""
Simulation Engine - Glucose Prediction and Treatment Simulation
This module provides the "brain" of the Digital Twin
"""

import numpy as np
from typing import Dict, List, Tuple
from digital_twin import DiabetesTwin


class GlucoseSimulator:
    """
    Simulates glucose levels and predicts future states
    """
    
    @staticmethod
    def predict_hba1c_change(
        twin: DiabetesTwin,
        lifestyle_changes: Dict[str, any],
        months: int = 6
    ) -> Tuple[float, str]:
        """
        Predict how HbA1c will change based on lifestyle modifications
        
        Args:
            twin: The patient's digital twin
            lifestyle_changes: Dict with keys like 'weight_loss_kg', 'exercise_increase', etc.
            months: Time horizon for prediction
        
        Returns:
            (predicted_hba1c, explanation)
        """
        current_hba1c = twin.metabolic_profile.hba1c_percent
        predicted_hba1c = current_hba1c
        changes = []
        
        # Weight loss effect
        # Medical fact: 5% body weight loss → 0.5% HbA1c reduction
        if 'weight_loss_kg' in lifestyle_changes:
            weight_loss = lifestyle_changes['weight_loss_kg']
            # Estimate current weight from BMI (assuming average height 170cm)
            estimated_weight = twin.demographics.bmi * (1.7 ** 2)
            weight_loss_pct = (weight_loss / estimated_weight) * 100
            hba1c_reduction = (weight_loss_pct / 5) * 0.5
            predicted_hba1c -= hba1c_reduction
            changes.append(f"Weight loss of {weight_loss}kg → -{hba1c_reduction:.2f}% HbA1c")
        
        # Exercise effect
        # Medical fact: 150 min/week moderate exercise → 0.6% HbA1c reduction
        if 'exercise_level_change' in lifestyle_changes:
            change = lifestyle_changes['exercise_level_change']
            if change == 'Low_to_Moderate':
                predicted_hba1c -= 0.4
                changes.append("Increased exercise (Low→Moderate) → -0.4% HbA1c")
            elif change == 'Low_to_High':
                predicted_hba1c -= 0.6
                changes.append("Increased exercise (Low→High) → -0.6% HbA1c")
            elif change == 'Moderate_to_High':
                predicted_hba1c -= 0.3
                changes.append("Increased exercise (Moderate→High) → -0.3% HbA1c")
        
        # Diet effect
        # Calorie reduction
        if 'calorie_reduction' in lifestyle_changes:
            cal_reduction = lifestyle_changes['calorie_reduction']
            # Rough estimate: 500 cal/day deficit → 0.3% HbA1c reduction
            hba1c_reduction = (cal_reduction / 500) * 0.3
            predicted_hba1c -= hba1c_reduction
            changes.append(f"Reduced calories by {cal_reduction}/day → -{hba1c_reduction:.2f}% HbA1c")
        
        # Smoking cessation
        if lifestyle_changes.get('quit_smoking', False):
            if twin.lifestyle.smoking_status == 'Current':
                predicted_hba1c -= 0.2
                changes.append("Quit smoking → -0.2% HbA1c")
        
        # Alcohol reduction
        if lifestyle_changes.get('reduce_alcohol', False):
            if twin.lifestyle.alcohol_consumption == 'Heavy':
                predicted_hba1c -= 0.15
                changes.append("Reduced alcohol (Heavy→Moderate) → -0.15% HbA1c")
        
        # Natural progression (if no changes, diabetes typically worsens)
        if not lifestyle_changes:
            natural_progression = 0.1 * (months / 6)  # 0.1% per 6 months
            predicted_hba1c += natural_progression
            changes.append(f"Natural progression over {months} months → +{natural_progression:.2f}% HbA1c")
        
        # Ensure realistic bounds
        predicted_hba1c = max(4.0, min(predicted_hba1c, 15.0))
        
        explanation = "\n".join(changes) if changes else "No changes predicted"
        
        return predicted_hba1c, explanation
    
    @staticmethod
    def simulate_meal_response(
        fasting_glucose: float,
        carbs_grams: float,
        insulin_sensitivity: float = 1.0,
        hours: int = 4
    ) -> List[Dict]:
        """
        Simulate glucose response to a meal
        
        Args:
            fasting_glucose: Starting glucose level (mg/dL)
            carbs_grams: Amount of carbohydrates eaten
            insulin_sensitivity: 1.0 = normal, <1.0 = resistant, >1.0 = sensitive
            hours: Duration to simulate
        
        Returns:
            List of {time, glucose} dictionaries
        """
        time_points = np.linspace(0, hours, hours * 12)  # Every 5 minutes
        glucose_curve = []
        
        # Carb impact factor (varies by insulin resistance)
        carb_impact = 3.0 / insulin_sensitivity  # mg/dL per gram of carb
        
        for t in time_points:
            if t < 0.5:  # First 30 min: rapid rise
                glucose = fasting_glucose + (carbs_grams * carb_impact * (t / 0.5))
            elif t < 2:  # 30min - 2hr: peak and decline
                peak = fasting_glucose + (carbs_grams * carb_impact)
                glucose = peak - ((peak - fasting_glucose) * ((t - 0.5) / 1.5))
            else:  # After 2hr: return to baseline
                excess = 20 * np.exp(-(t - 2))
                glucose = fasting_glucose + excess
            
            glucose_curve.append({
                'time_hours': round(t, 2),
                'glucose_mgdl': round(glucose, 1)
            })
        
        return glucose_curve
    
    @staticmethod
    def calculate_insulin_resistance(twin: DiabetesTwin) -> float:
        """
        Estimate insulin resistance level
        
        Returns:
            Resistance factor (1.0 = normal, higher = more resistant)
        """
        resistance = 1.0
        
        # BMI effect
        if twin.demographics.bmi >= 35:
            resistance *= 1.5
        elif twin.demographics.bmi >= 30:
            resistance *= 1.3
        elif twin.demographics.bmi >= 25:
            resistance *= 1.1
        
        # Waist circumference (central obesity)
        if twin.demographics.gender == 'Male':
            if twin.demographics.waist_circumference_cm >= 102:
                resistance *= 1.2
        else:  # Female
            if twin.demographics.waist_circumference_cm >= 88:
                resistance *= 1.2
        
        # HbA1c (higher = more resistant)
        if twin.metabolic_profile.hba1c_percent >= 9.0:
            resistance *= 1.4
        elif twin.metabolic_profile.hba1c_percent >= 7.5:
            resistance *= 1.2
        
        # Activity level (exercise improves sensitivity)
        if twin.lifestyle.physical_activity_level == 'High':
            resistance *= 0.85
        elif twin.lifestyle.physical_activity_level == 'Low':
            resistance *= 1.15
        
        return round(resistance, 2)


class RiskAssessor:
    """
    Assesses long-term complication risks using evidence-based models.
    Based on UKPDS Risk Engine principles and clinical diabetes literature.
    """
    
    @staticmethod
    def predict_complication_risk(
        twin: DiabetesTwin,
        years_ahead: int = 5
    ) -> Dict[str, Dict]:
        """
        Predict risk of complications over time using evidence-based models.
        
        Medical basis:
        - HbA1c: Each 1% increase = 30-40% higher complication risk
        - Duration matters: Cumulative exposure to hyperglycemia
        
        Returns:
            Dictionary with risk predictions for each complication
        """
        risks = {}
        hba1c = twin.metabolic_profile.hba1c_percent
        age = twin.demographics.age
        bp_sys = twin.complications_status.bp_systolic
        
        # RETINOPATHY - Highly HbA1c dependent
        # Each 1% above 6.0 adds significant risk, non-linear with time
        retinopathy_base = max(0, (hba1c - 6.0) * 12)
        retinopathy_time_factor = years_ahead ** 1.3 if years_ahead > 0 else 0
        retinopathy_bp = 15 if bp_sys >= 140 else 5 if bp_sys >= 130 else 0
        retinopathy_score = retinopathy_base + retinopathy_time_factor + retinopathy_bp
        
        risks['retinopathy'] = {
            'risk_level': 'high' if retinopathy_score > 50 else 'moderate' if retinopathy_score > 25 else 'low',
            'risk_score': min(100, max(0, int(retinopathy_score))),
            'probability': f"{min(95, int(retinopathy_score * 0.8))}%",
            'recommendation': 'URGENT: Dilated eye exam now, possible laser treatment' if retinopathy_score > 50 else 
                             'Annual eye exam required' if retinopathy_score > 25 else 'Eye exam every 2 years'
        }
        
        # NEPHROPATHY - BP and HbA1c dependent
        nephropathy_base = max(0, (hba1c - 6.5) * 10)
        nephropathy_bp = 20 if bp_sys >= 140 else 10 if bp_sys >= 130 else 0
        nephropathy_ggt = 15 if twin.complications_status.ggt >= 50 else 5 if twin.complications_status.ggt >= 35 else 0
        nephropathy_urate = 10 if twin.complications_status.serum_urate >= 7.0 else 0
        nephropathy_time = years_ahead * 4
        nephropathy_score = nephropathy_base + nephropathy_bp + nephropathy_ggt + nephropathy_urate + nephropathy_time
        
        risks['nephropathy'] = {
            'risk_level': 'high' if nephropathy_score > 50 else 'moderate' if nephropathy_score > 25 else 'low',
            'risk_score': min(100, max(0, int(nephropathy_score))),
            'probability': f"{min(90, int(nephropathy_score * 0.7))}%",
            'recommendation': 'URGENT: Nephrology referral, check GFR/ACR, consider ACE inhibitor' if nephropathy_score > 50 else 
                             'Check kidney function every 6 months' if nephropathy_score > 25 else 'Annual kidney check'
        }
        
        # CARDIOVASCULAR - Multi-factorial (UKPDS-based)
        cv_age_factor = max(0, (age - 40) * 1.5)
        cv_hba1c_factor = max(0, (hba1c - 6.0) * 8)
        cv_smoking = 25 if twin.lifestyle.smoking_status == 'Current' else 10 if twin.lifestyle.smoking_status == 'Former' else 0
        cv_lipids = 20 if twin.complications_status.cholesterol_ldl >= 160 else 12 if twin.complications_status.cholesterol_ldl >= 130 else 5 if twin.complications_status.cholesterol_ldl >= 100 else 0
        cv_hdl_penalty = 10 if twin.complications_status.cholesterol_hdl < 40 else 0
        cv_bp = 15 if bp_sys >= 140 else 8 if bp_sys >= 130 else 0
        cv_bmi = 12 if twin.demographics.bmi >= 35 else 8 if twin.demographics.bmi >= 30 else 3 if twin.demographics.bmi >= 25 else 0
        cv_family = 8 if twin.risk_factors.family_history_diabetes else 0
        cv_time = years_ahead * 3
        
        cv_score = cv_age_factor + cv_hba1c_factor + cv_smoking + cv_lipids + cv_hdl_penalty + cv_bp + cv_bmi + cv_family + cv_time
        
        risks['cardiovascular'] = {
            'risk_level': 'high' if cv_score > 60 else 'moderate' if cv_score > 30 else 'low',
            'risk_score': min(100, max(0, int(cv_score))),
            '10_year_risk': f"{min(85, int(cv_score * 0.6))}%",
            'recommendation': 'URGENT: Cardiology consult, initiate statin + aspirin, strict BP control' if cv_score > 60 else 
                             'Monitor BP and lipids closely, lifestyle intervention' if cv_score > 30 else 'Continue preventive care'
        }
        
        # NEUROPATHY - Duration and HbA1c are primary drivers
        neuropathy_base = max(0, (hba1c - 6.5) * 8)
        neuropathy_duration = years_ahead * 5
        neuropathy_age = 10 if age > 60 else 5 if age > 50 else 0
        neuropathy_alcohol = 8 if twin.lifestyle.alcohol_consumption == 'Heavy' else 0
        neuropathy_score = neuropathy_base + neuropathy_duration + neuropathy_age + neuropathy_alcohol
        
        risks['neuropathy'] = {
            'risk_level': 'high' if neuropathy_score > 45 else 'moderate' if neuropathy_score > 20 else 'low',
            'risk_score': min(100, max(0, int(neuropathy_score))),
            'recommendation': 'Foot exam every visit, monofilament testing, check for ulcers' if neuropathy_score > 45 else 
                             'Annual comprehensive foot examination' if neuropathy_score > 20 else 'Standard diabetes foot care'
        }
        
        return risks
    
    @staticmethod
    def predict_organ_function(twin: DiabetesTwin, years_ahead: int = 0) -> Dict[str, float]:
        """
        Predict organ function levels (0.0 to 1.0) based on disease progression.
        Returns estimated function levels for 3D visualization.
        
        Function levels:
        - 1.0 = Fully healthy
        - 0.7+ = Good function
        - 0.4-0.7 = Impaired function  
        - <0.4 = Severely compromised
        """
        hba1c = twin.metabolic_profile.hba1c_percent
        bp_sys = twin.complications_status.bp_systolic
        age = twin.demographics.age
        
        # Pancreas beta-cell function
        # Higher HbA1c = more beta-cell burnout (glucotoxicity)
        base_pancreas = max(0.3, 1.0 - ((hba1c - 5.0) * 0.07))
        # Degradation accelerates with poor control
        degradation_rate = 0.035 * (1 + max(0, (hba1c - 7) * 0.15))
        pancreas_degradation = years_ahead * degradation_rate
        pancreas_function = max(0.1, base_pancreas - pancreas_degradation)
        
        # Kidney function (eGFR-based proxy)
        kidney_risk_factors = sum([
            0.12 if bp_sys >= 140 else 0.05 if bp_sys >= 130 else 0,
            0.10 if hba1c >= 9.0 else 0.05 if hba1c >= 7.5 else 0,
            0.08 if twin.complications_status.ggt >= 50 else 0.03 if twin.complications_status.ggt >= 35 else 0,
            0.05 if twin.complications_status.serum_urate >= 7.0 else 0,
        ])
        kidney_degradation = years_ahead * 0.025 * (1 + kidney_risk_factors)
        kidney_function = max(0.2, 1.0 - kidney_risk_factors - kidney_degradation)
        
        # Eye (retina) health
        eye_risk = max(0, (hba1c - 6.0) * 0.05) + (0.08 if bp_sys >= 140 else 0.03 if bp_sys >= 130 else 0)
        eye_degradation = years_ahead * 0.03
        eye_function = max(0.2, 1.0 - eye_risk - eye_degradation)
        
        # Heart health
        heart_risk = sum([
            0.12 if twin.lifestyle.smoking_status == 'Current' else 0.05 if twin.lifestyle.smoking_status == 'Former' else 0,
            0.08 if twin.complications_status.cholesterol_ldl >= 160 else 0.04 if twin.complications_status.cholesterol_ldl >= 130 else 0,
            0.06 if bp_sys >= 140 else 0.03 if bp_sys >= 130 else 0,
            0.05 if twin.demographics.bmi >= 35 else 0.03 if twin.demographics.bmi >= 30 else 0,
            0.03 if age > 60 else 0.01 if age > 50 else 0,
        ])
        heart_degradation = years_ahead * 0.02
        heart_function = max(0.3, 1.0 - heart_risk - heart_degradation)
        
        # Vascular health (glycation of blood vessels)
        vessel_glycation = min(1.0, (hba1c - 5) / 10)
        vessel_degradation = years_ahead * 0.025
        vessel_function = max(0.2, 1.0 - vessel_glycation * 0.5 - vessel_degradation)
        
        # Nerve function (peripheral neuropathy)
        nerve_base = max(0.4, 1.0 - ((hba1c - 6.0) * 0.06))
        nerve_degradation = years_ahead * 0.04
        nerve_function = max(0.2, nerve_base - nerve_degradation)
        
        return {
            'pancreas': round(pancreas_function, 2),
            'kidneys': round(kidney_function, 2),
            'eyes': round(eye_function, 2),
            'heart': round(heart_function, 2),
            'vessels': round(vessel_function, 2),
            'nerves': round(nerve_function, 2)
        }


class MedicationSimulator:
    """
    Simulates the effect of different diabetes medications
    """
    
    # Knowledge Base: Drug Effects
    DRUG_EFFECTS = {
        "metformin": {
            "hba1c_drop": 1.5,      # % reduction
            "weight_change": -2.0,  # kg
            "hypo_risk": "Low",
            "mechanism": "Reduces liver glucose production"
        },
        "sulfonylurea": {
            "hba1c_drop": 1.5,
            "weight_change": 2.0,   # Weight gain common
            "hypo_risk": "Moderate",
            "mechanism": "Stimulates insulin release"
        },
        "dpp4_inhibitor": {
            "hba1c_drop": 0.7,
            "weight_change": 0.0,   # Neutral
            "hypo_risk": "Low",
            "mechanism": "Increases incretin levels"
        },
        "sglt2_inhibitor": {
            "hba1c_drop": 0.8,
            "weight_change": -3.0,  # Weight loss
            "hypo_risk": "Low",
            "mechanism": "Excretes glucose in urine"
        },
        "glp1_agonist": {
            "hba1c_drop": 1.2,
            "weight_change": -4.0,  # Significant weight loss
            "hypo_risk": "Low",
            "mechanism": "Slows digestion, increases satiety"
        },
        "insulin_basal": {
            "hba1c_drop": 2.5,
            "weight_change": 3.0,
            "hypo_risk": "High",
            "mechanism": "Direct glucose uptake"
        }
    }

    @staticmethod
    def simulate_treatment(current_hba1c: float, drugs: List[str]) -> Dict:
        """
        Predict outcome of a drug combination
        """
        predicted_hba1c = current_hba1c
        total_weight_change = 0.0
        risks = []
        mechanisms = []
        
        synergy_factor = 1.0
        
        for drug in drugs:
            drug_key = drug.lower().replace(" ", "_")
            if drug_key in MedicationSimulator.DRUG_EFFECTS:
                effect = MedicationSimulator.DRUG_EFFECTS[drug_key]
                
                # Apply effect (diminishing returns for multiple drugs)
                drop = effect['hba1c_drop'] * synergy_factor
                predicted_hba1c -= drop
                
                total_weight_change += effect['weight_change']
                mechanisms.append(effect['mechanism'])
                
                if effect['hypo_risk'] in ["Moderate", "High"]:
                    risks.append(f"{effect['hypo_risk']} risk of Hypoglycemia with {drug}")
                
                # Reduce efficacy for next drug added
                synergy_factor *= 0.7 
            else:
                risks.append(f"Unknown drug: {drug}")

        # Bounds
        predicted_hba1c = max(5.0, predicted_hba1c)

        return {
            "original_hba1c": current_hba1c,
            "predicted_hba1c": round(predicted_hba1c, 2),
            "hba1c_reduction": round(current_hba1c - predicted_hba1c, 2),
            "weight_impact_kg": round(total_weight_change, 1),
            "mechanisms": mechanisms,
            "warnings": risks
        }

if __name__ == "__main__":
    import pandas as pd
    from digital_twin import DiabetesTwin
    
    # Load patient
    df = pd.read_csv('diabetes_dataset.csv')
    sample_patient = df.iloc[0].to_dict()
    twin = DiabetesTwin(patient_id="DM_00001", patient_data=sample_patient)
    
    print("="*70)
    print("GLUCOSE SIMULATION ENGINE - DEMO")
    print("="*70)
    
    # Test 1: Predict HbA1c change with lifestyle modifications
    print("\n📊 SCENARIO 1: Patient loses 10kg and increases exercise")
    print("-" * 70)
    
    lifestyle_changes = {
        'weight_loss_kg': 10,
        'exercise_level_change': 'Low_to_Moderate',
        'calorie_reduction': 500
    }
    
    predicted_hba1c, explanation = GlucoseSimulator.predict_hba1c_change(
        twin, lifestyle_changes, months=6
    )
    
    print(f"Current HbA1c: {twin.metabolic_profile.hba1c_percent:.1f}%")
    print(f"Predicted HbA1c (6 months): {predicted_hba1c:.1f}%")
    print(f"\nBreakdown:")
    print(explanation)
    
    # Test 2: Simulate meal response
    print("\n\n🍽️  SCENARIO 2: Patient eats 50g carbs (e.g., rice)")
    print("-" * 70)
    
    resistance = GlucoseSimulator.calculate_insulin_resistance(twin)
    print(f"Insulin Resistance Factor: {resistance}x")
    
    meal_curve = GlucoseSimulator.simulate_meal_response(
        fasting_glucose=twin.metabolic_profile.fasting_glucose_mgdl,
        carbs_grams=50,
        insulin_sensitivity=1/resistance
    )
    
    print(f"\nGlucose Response:")
    for point in meal_curve[::12]:  # Show every hour
        print(f"  {point['time_hours']:.1f}h: {point['glucose_mgdl']:.0f} mg/dL")
    
    # Test 3: Long-term risk assessment
    print("\n\n⚠️  SCENARIO 3: 5-Year Complication Risk")
    print("-" * 70)
    
    risks = RiskAssessor.predict_complication_risk(twin, years_ahead=5)
    
    for complication, data in risks.items():
        print(f"\n{complication.upper()}:")
        print(f"  Risk Level: {data['risk_level'].upper()}")
        print(f"  Risk Score: {data['risk_score']}/100")
        print(f"  Action: {data['recommendation']}")
