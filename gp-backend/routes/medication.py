"""
Medication routes for MedTwin
Handles medication management and NotifierAgent interactions
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.medication import Medication
from models.user import User
from database import db
from agents import get_notifier_agent
from datetime import datetime

medication_bp = Blueprint('medication', __name__)

from models.user import Patient, Doctor

@medication_bp.route('/', methods=['POST'])
@jwt_required()
def add_medication():
    """Add a new medication"""
    try:
        identity = get_jwt_identity()
        patient = Patient.get_by_identity(identity)
        if not patient or patient.role != 'patient':
            return jsonify({'error': 'Unauthorized'}), 401
        user_id = patient.id
        
        data = request.get_json()
        
        # Parse start date
        start_date_str = data.get('startDate', datetime.now().strftime('%Y-%m-%d'))
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except:
            start_date = datetime.now().date()
        
        # Create medication
        medication = Medication(
            patient_id=user_id,
            name=data.get('name'),
            dosage=data.get('dosage'),
            frequency=data.get('frequency'),
            timing=data.get('timing', []),
            instructions=data.get('instructions'),
            start_date=start_date,
            duration=data.get('duration', 'ongoing'),
            active=True
        )
        
        db.session.add(medication)
        db.session.commit()
        
        # Add to notifier agent
        notifier = get_notifier_agent()
        notifier.add_medication({
            'id': medication.id,
            'name': medication.name,
            'dosage': medication.dosage,
            'frequency': medication.frequency,
            'timing': medication.timing,
            'instructions': medication.instructions,
            'start_date': start_date_str,
            'duration': medication.duration
        })
        
        return jsonify({
            'ok': True,
            'medication': medication.to_dict(),
            'message': f'Added {medication.name} to your medication schedule'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Add medication failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@medication_bp.route('/', methods=['GET'])
@jwt_required()
def list_medications():
    """List all medications for current user"""
    try:
        identity = get_jwt_identity()
        patient = Patient.get_by_identity(identity)
        if not patient or patient.role != 'patient':
            return jsonify({'error': 'Unauthorized'}), 401
        user_id = patient.id
        
        medications = Medication.query.filter_by(
            patient_id=user_id,
            active=True
        ).order_by(Medication.created_at.desc()).all()
        
        return jsonify({
            'ok': True,
            'medications': [m.to_dict() for m in medications]
        }), 200
        
    except Exception as e:
        print(f"[ERROR] List medications failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@medication_bp.route('/<int:medication_id>', methods=['PUT'])
@jwt_required()
def update_medication(medication_id):
    """Update a medication"""
    try:
        identity = get_jwt_identity()
        patient = Patient.get_by_identity(identity)
        if not patient or patient.role != 'patient':
            return jsonify({'error': 'Unauthorized'}), 401
        user_id = patient.id
        
        data = request.get_json()
        
        medication = Medication.query.filter_by(
            id=medication_id,
            patient_id=user_id
        ).first()
        
        if not medication:
            return jsonify({'error': 'Medication not found'}), 404
        
        # Update fields
        if 'name' in data:
            medication.name = data['name']
        if 'dosage' in data:
            medication.dosage = data['dosage']
        if 'frequency' in data:
            medication.frequency = data['frequency']
        if 'timing' in data:
            medication.timing = data['timing']
        if 'instructions' in data:
            medication.instructions = data['instructions']
        if 'duration' in data:
            medication.duration = data['duration']
        if 'active' in data:
            medication.active = data['active']
        
        medication.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'ok': True,
            'medication': medication.to_dict(),
            'message': 'Medication updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Update medication failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@medication_bp.route('/<int:medication_id>', methods=['DELETE'])
@jwt_required()
def delete_medication(medication_id):
    """Delete (deactivate) a medication"""
    try:
        identity = get_jwt_identity()
        patient = Patient.get_by_identity(identity)
        if not patient or patient.role != 'patient':
            return jsonify({'error': 'Unauthorized'}), 401
        user_id = patient.id
        
        medication = Medication.query.filter_by(
            id=medication_id,
            patient_id=user_id
        ).first()
        
        if not medication:
            return jsonify({'error': 'Medication not found'}), 404
        
        # Soft delete
        medication.active = False
        medication.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'ok': True,
            'message': 'Medication deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Delete medication failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@medication_bp.route('/schedule', methods=['GET'])
@jwt_required()
def get_schedule():
    """Get medication schedule"""
    try:
        identity = get_jwt_identity()
        patient = Patient.get_by_identity(identity)
        if not patient or patient.role != 'patient':
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get notifier agent
        notifier = get_notifier_agent()
        
        # Generate schedule
        schedule = notifier.generate_medication_schedule()
        
        return jsonify({
            'ok': True,
            'schedule': schedule
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get schedule failed: {str(e)}")
        return jsonify({'error': str(e)}), 500
