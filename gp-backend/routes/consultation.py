"""
Consultation routes for medical interview
Handles SymptomQAAgent and AnalysisAgent interactions
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.consultation import Consultation
from models.user import User
from database import db
from agents import get_symptom_agent, get_analysis_agent

consultation_bp = Blueprint('consultation', __name__)

# Store active agent sessions (in production, use Redis or database)
active_sessions = {}

from models.user import Patient, Doctor

@consultation_bp.route('/start', methods=['POST'])
@jwt_required()
def start_consultation():
    """Start a new medical consultation"""
    try:
        identity = get_jwt_identity()
        patient = Patient.get_by_identity(identity)
        
        if not patient or patient.role != 'patient':
            return jsonify({'error': 'Unauthorized. Only patients can start consultations.'}), 403
            
        user_id = patient.id
        data = request.get_json()
        
        initial_message = data.get('message', 'I need medical help')
        
        # Create new consultation in database
        consultation = Consultation(
            patient_id=user_id,
            status='active',
            conversation_history=[],
            collected_data={}
        )
        db.session.add(consultation)
        db.session.commit()
        
        # Get symptom agent (Create NEW instance to avoid shared state)
        from agents.medtwin_agents import SymptomQAAgent
        from agents import get_llm
        agent = SymptomQAAgent(get_llm())
        
        # Start interview
        response_text = agent.start_interview(initial_message)
        
        # Store session
        active_sessions[consultation.id] = agent
        
        # Update conversation history
        consultation.conversation_history = [
            {'role': 'user', 'content': initial_message},
            {'role': 'assistant', 'content': response_text}
        ]
        db.session.commit()
        
        return jsonify({
            'ok': True,
            'consultationId': consultation.id,
            'response': response_text,
            'completed': agent.interview_complete
        }), 201
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"[ERROR] Start consultation failed: {str(e)}"
        print(error_msg)
        print(f"[ERROR] Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': error_msg, 'type': type(e).__name__}), 500

@consultation_bp.route('/<int:consultation_id>/continue', methods=['POST'])
# @jwt_required()
def continue_consultation(consultation_id):
    """Continue an existing consultation"""
    try:
        # user_id = get_jwt_identity()
        user_id = 1 # Mock user for testing
        data = request.get_json()
        
        message = data.get('message', '')
        
        # Get consultation
        consultation = Consultation.query.filter_by(
            id=consultation_id,
            patient_id=user_id
        ).first()
        
        if not consultation:
            return jsonify({'error': 'Consultation not found'}), 404
        
        # Get agent from session
        agent = active_sessions.get(consultation_id)
        if not agent:
            return jsonify({'error': 'Session expired. Please start a new consultation.'}), 400
        
        # Continue interview
        response_text = agent.continue_interview(message)
        
        # Update conversation history
        if not consultation.conversation_history:
            consultation.conversation_history = []
        
        consultation.conversation_history.append({'role': 'user', 'content': message})
        consultation.conversation_history.append({'role': 'assistant', 'content': response_text})
        
        # Update collected data
        consultation.collected_data = agent.get_collected_data()
        
        # Check if completed
        if agent.interview_complete:
            consultation.status = 'completed'
            # Remove from active sessions
            if consultation_id in active_sessions:
                del active_sessions[consultation_id]
        
        db.session.commit()
        
        return jsonify({
            'ok': True,
            'response': response_text,
            'completed': agent.interview_complete,
            'collectedData': consultation.collected_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Continue consultation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@consultation_bp.route('/<int:consultation_id>', methods=['GET'])
# @jwt_required()
def get_consultation(consultation_id):
    """Get consultation details"""
    try:
        # user_id = get_jwt_identity()
        user_id = 1
        
        consultation = Consultation.query.filter_by(
            id=consultation_id,
            patient_id=user_id
        ).first()
        
        if not consultation:
            return jsonify({'error': 'Consultation not found'}), 404
        
        return jsonify({
            'ok': True,
            'consultation': consultation.to_dict()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get consultation failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@consultation_bp.route('/<int:consultation_id>/analyze', methods=['POST'])
# @jwt_required()
def analyze_consultation(consultation_id):
    """Analyze completed consultation"""
    try:
        # user_id = get_jwt_identity()
        user_id = 1 # Mock user for testing
        
        consultation = Consultation.query.filter_by(
            id=consultation_id,
            patient_id=user_id
        ).first()
        
        if not consultation:
            return jsonify({'error': 'Consultation not found'}), 404
        
        # Get analysis agent
        analysis_agent = get_analysis_agent()
        
        # Analyze collected data
        analysis = analysis_agent.analyze(consultation.collected_data)
        
        # Store analysis result
        consultation.analysis_result = analysis
        consultation.status = 'analyzed'
        db.session.commit()
        
        return jsonify({
            'ok': True,
            'analysis': analysis
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Analyze consultation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@consultation_bp.route('/<int:consultation_id>/plan', methods=['POST'])
# @jwt_required()
def plan_consultation(consultation_id):
    """Generate treatment plan using PlanningAgent"""
    try:
        # user_id = get_jwt_identity()
        user_id = 1
        
        consultation = Consultation.query.filter_by(
            id=consultation_id,
            patient_id=user_id
        ).first()
        
        if not consultation or not consultation.analysis_result:
            return jsonify({'error': 'Consultation analysis not found. Analyze first.'}), 400
        
        # Get planning agent
        from agents import get_planning_agent
        planning_agent = get_planning_agent()
        
        # Create comprehensive plan
        plan = planning_agent.create_comprehensive_plan(consultation.analysis_result)
        
        # Store plan
        consultation.care_plan = plan
        consultation.status = 'planned'
        db.session.commit()
        
        return jsonify({
            'ok': True,
            'plan': plan
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Plan consultation failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@consultation_bp.route('/list', methods=['GET'])
# @jwt_required()
def list_consultations():
    """List all consultations for current user"""
    try:
        # user_id = get_jwt_identity()
        user_id = 1
        
        consultations = Consultation.query.filter_by(patient_id=user_id).order_by(
            Consultation.created_at.desc()
        ).all()
        
        return jsonify({
            'ok': True,
            'consultations': [c.to_dict() for c in consultations]
        }), 200
        
    except Exception as e:
        print(f"[ERROR] List consultations failed: {str(e)}")
        return jsonify({'error': str(e)}), 500
