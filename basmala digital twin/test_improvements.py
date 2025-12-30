"""
Test script for MedTwin improvements
"""
import pandas as pd
from simulation_engine import RiskAssessor, GlucoseSimulator
from digital_twin import DiabetesTwin

# Load dataset
df = pd.read_csv('diabetes_dataset.csv')

# Test with first patient (high HbA1c patient)
print("=" * 70)
print("MEDTWIN IMPROVEMENT TEST")
print("=" * 70)

patient_data = df.iloc[0].to_dict()
twin = DiabetesTwin("DM_00000", patient_data)

print(f"\nPatient: {twin.patient_id}")
print(f"Age: {twin.demographics.age}, Gender: {twin.demographics.gender}")
print(f"HbA1c: {twin.metabolic_profile.hba1c_percent}%")
print(f"BP: {twin.complications_status.bp_systolic}/{twin.complications_status.bp_diastolic}")
print(f"BMI: {twin.demographics.bmi}")

# Test organ function predictions
print("\n" + "-" * 70)
print("ORGAN FUNCTION PREDICTIONS")
print("-" * 70)

for years in [0, 3, 5, 10]:
    funcs = RiskAssessor.predict_organ_function(twin, years)
    print(f"\nYear {2025 + years} (+{years}y):")
    print(f"  Pancreas: {funcs['pancreas']*100:.0f}%  |  Heart: {funcs['heart']*100:.0f}%  |  Kidneys: {funcs['kidneys']*100:.0f}%")
    print(f"  Eyes: {funcs['eyes']*100:.0f}%  |  Vessels: {funcs['vessels']*100:.0f}%  |  Nerves: {funcs['nerves']*100:.0f}%")

# Test risk predictions
print("\n" + "-" * 70)  
print("COMPLICATION RISK PREDICTIONS")
print("-" * 70)

for years in [0, 5, 10]:
    risks = RiskAssessor.predict_complication_risk(twin, years)
    print(f"\nYear {2025 + years} (+{years}y):")
    for comp, data in risks.items():
        print(f"  {comp.title()}: {data['risk_level'].upper()} ({data['risk_score']}/100) - {data['recommendation'][:50]}...")

print("\n" + "=" * 70)
print("TEST COMPLETE - All systems working!")
print("=" * 70)
