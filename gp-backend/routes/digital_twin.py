"""
Digital Twin Simulation Routes
Handles 3D visualization and health simulation
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from database import db
import random

digital_twin_bp = Blueprint('digital_twin', __name__)


def calculate_health_score(patient_data):
    """
    Calculate overall health score based on patient conditions and vitals
    """
    base_score = 100
    
    # Deduct points based on conditions
    conditions = patient_data.get('conditions', [])
    if isinstance(conditions, str):
        conditions = [conditions]
    
    condition_penalty = {
        'diabetes': 15,
        'hypertension': 12,
        'heart_disease': 20,
        'copd': 18,
        'asthma': 10
    }
    
    for condition in conditions:
        condition_lower = condition.lower()
        for key, penalty in condition_penalty.items():
            if key in condition_lower:
                base_score -= penalty
                break
    
    # Adjust based on age
    age = patient_data.get('age', 30)
    if age > 60:
        base_score -= 5
    elif age > 70:
        base_score -= 10
    
    # Adjust based on glucose (if diabetic)
    glucose = patient_data.get('glucose', 100)
    if glucose > 140:
        base_score -= 10
    elif glucose < 70:
        base_score -= 5
    
    # Ensure score is within bounds
    return max(0, min(100, base_score))


def generate_risk_factors(patient_data):
    """
    Generate personalized risk factors based on patient data
    """
    risks = []
    conditions = patient_data.get('conditions', [])
    if isinstance(conditions, str):
        conditions = [conditions]
    
    age = patient_data.get('age', 30)
    glucose = patient_data.get('glucose', 100)
    
    for condition in conditions:
        condition_lower = condition.lower()
        
        if 'diabetes' in condition_lower:
            if glucose > 140:
                risks.append('High blood glucose levels detected - risk of complications')
            risks.append('Monitor for diabetic neuropathy and retinopathy')
            
        if 'hypertension' in condition_lower or 'blood pressure' in condition_lower:
            risks.append('Cardiovascular strain - monitor blood pressure regularly')
            risks.append('Increased risk of stroke and heart attack')
            
        if 'heart' in condition_lower or 'cardiac' in condition_lower:
            risks.append('Cardiac function requires close monitoring')
            risks.append('Risk of heart failure if untreated')
            
        if 'copd' in condition_lower:
            risks.append('Respiratory function decline - avoid triggers')
            risks.append('Risk of acute exacerbations')
            
        if 'asthma' in condition_lower:
            risks.append('Monitor for asthma triggers and symptoms')
    
    if age > 60:
        risks.append('Age-related metabolic changes - adjust treatment accordingly')
    
    if not risks:
        risks.append('No major risk factors identified - maintain current health routine')
    
    return risks[:5]  # Return top 5 risks


def generate_recommendations(patient_data):
    """
    Generate personalized health recommendations
    """
    recommendations = []
    conditions = patient_data.get('conditions', [])
    if isinstance(conditions, str):
        conditions = [conditions]
    
    glucose = patient_data.get('glucose', 100)
    
    for condition in conditions:
        condition_lower = condition.lower()
        
        if 'diabetes' in condition_lower:
            recommendations.append('Maintain consistent blood glucose monitoring (at least twice daily)')
            if glucose > 140:
                recommendations.append('Consider adjusting insulin dosage or medication - consult your doctor')
            recommendations.append('Follow a balanced low-GI diet and regular exercise routine')
            
        if 'hypertension' in condition_lower:
            recommendations.append('Reduce sodium intake and maintain DASH diet')
            recommendations.append('Practice stress-reduction techniques (meditation, yoga)')
            recommendations.append('Monitor blood pressure daily at same time')
            
        if 'heart' in condition_lower:
            recommendations.append('Engage in moderate aerobic exercise (30 min, 5x/week)')
            recommendations.append('Avoid excessive salt and saturated fats')
            recommendations.append('Take prescribed cardiac medications as directed')
            
        if 'copd' in condition_lower or 'asthma' in condition_lower:
            recommendations.append('Avoid smoke, dust, and air pollutants')
            recommendations.append('Practice breathing exercises daily')
            recommendations.append('Keep rescue inhaler accessible at all times')
    
    # General recommendations
    recommendations.append('Schedule regular check-ups with your healthcare provider')
    recommendations.append('Stay hydrated - aim for 8 glasses of water daily')
    
    return recommendations[:6]  # Return top 6 recommendations


def determine_status(health_score):
    """
    Determine overall health status based on score
    """
    if health_score >= 80:
        return 'Excellent - Continue current health routine'
    elif health_score >= 70:
        return 'Good - Minor adjustments recommended'
    elif health_score >= 60:
        return 'Fair - Requires attention and lifestyle modifications'
    elif health_score >= 50:
        return 'Poor - Immediate medical consultation recommended'
    else:
        return 'Critical - Seek immediate medical attention'


@digital_twin_bp.route('/simulate', methods=['POST'])
@jwt_required()
def simulate_digital_twin():
    """
    Run digital twin simulation for patient
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get request data
        data = request.get_json()
        
        # Build patient profile
        patient_data = {
            'patient_id': user.id,
            'conditions': data.get('conditions', user.diseases or []),
            'age': data.get('age', user.age or 30),
            'glucose': data.get('glucose', 100),
            'blood_pressure': data.get('blood_pressure', '120/80')
        }
        
        # Calculate health metrics
        health_score = calculate_health_score(patient_data)
        risk_factors = generate_risk_factors(patient_data)
        recommendations = generate_recommendations(patient_data)
        overall_status = determine_status(health_score)
        
        # Simulate organ-specific data
        organ_data = {
            'heart': {
                'health': random.randint(60, 95),
                'status': 'Functional',
                'notes': 'Regular rhythm detected'
            },
            'kidneys': {
                'health': random.randint(70, 95),
                'status': 'Filtering normally',
                'notes': 'No significant impairment'
            },
            'pancreas': {
                'health': random.randint(50, 85) if 'diabetes' in str(patient_data.get('conditions')).lower() else random.randint(80, 95),
                'status': 'Insulin production monitored',
                'notes': 'Requires glucose regulation'
            },
            'vessels': {
                'health': random.randint(65, 90),
                'status': 'Blood flow adequate',
                'notes': 'Monitor for atherosclerosis'
            }
        }
        
        response_data = {
            'success': True,
            'patient_id': user.id,
            'health_score': health_score,
            'overall_status': overall_status,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'organ_data': organ_data,
            'simulation_timestamp': 'now',  # In production, use datetime.now().isoformat()
            'message': 'Simulation completed successfully'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"[ERROR] Digital Twin Simulation failed: {str(e)}")
        return jsonify({'error': 'Simulation failed', 'details': str(e)}), 500


@digital_twin_bp.route('/history', methods=['GET'])
@jwt_required()
def get_simulation_history():
    """
    Get simulation history for current user
    """
    try:
        current_user_id = get_jwt_identity()
        
        # In a full implementation, this would query a SimulationHistory table
        # For now, return a mock history
        history = [
            {
                'timestamp': '2025-12-29T10:00:00',
                'health_score': 78,
                'status': 'Good'
            }
        ]
        
        return jsonify({'success': True, 'history': history}), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch simulation history: {str(e)}")
        return jsonify({'error': 'Failed to fetch history', 'details': str(e)}), 500


@digital_twin_bp.route('/organs/<organ_name>', methods=['GET'])
@jwt_required()
def get_organ_details(organ_name):
    """
    Get detailed information about a specific organ
    """
    try:
        organ_info = {
            'heart': {
                'name': 'Heart',
                'function': 'Pumps blood throughout the body',
                'common_issues': ['Arrhythmia', 'Heart failure', 'Coronary artery disease'],
                'preventive_measures': ['Regular exercise', 'Healthy diet', 'Stress management']
            },
            'kidney': {
                'name': 'Kidneys',
                'function': 'Filter waste from blood and regulate fluid balance',
                'common_issues': ['Chronic kidney disease', 'Kidney stones', 'Infections'],
                'preventive_measures': ['Stay hydrated', 'Control blood pressure', 'Limit salt']
            },
            'pancreas': {
                'name': 'Pancreas',
                'function': 'Produces insulin and digestive enzymes',
                'common_issues': ['Diabetes', 'Pancreatitis', 'Pancreatic cancer'],
                'preventive_measures': ['Maintain healthy weight', 'Limit alcohol', 'Balanced diet']
            },
            'vessels': {
                'name': 'Vascular System',
                'function': 'Transports blood, oxygen, and nutrients',
                'common_issues': ['Atherosclerosis', 'Varicose veins', 'Blood clots'],
                'preventive_measures': ['Regular exercise', 'Avoid smoking', 'Healthy cholesterol levels']
            }
        }
        
        if organ_name not in organ_info:
            return jsonify({'error': 'Organ not found'}), 404
        
        return jsonify({'success': True, 'organ': organ_info[organ_name]}), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch organ details: {str(e)}")
        return jsonify({'error': 'Failed to fetch organ details', 'details': str(e)}), 500
