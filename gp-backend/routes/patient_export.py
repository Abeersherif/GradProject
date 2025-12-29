"""
Patient data export route
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.consultation import Consultation
from models.medication import Medication
from models.ticket import Ticket
from database import db
from utils.csv_export import export_patient_data
import os

patient_export_bp = Blueprint('patient_export', __name__)


from models.user import Patient

@patient_export_bp.route('/export-data', methods=['GET'])
@jwt_required()
def export_my_data():
    """Patient exports their own complete data"""
    try:
        identity = get_jwt_identity()
        patient = Patient.get_by_identity(identity)
        if not patient or patient.role != 'patient':
            return jsonify({'error': 'Unauthorized'}), 401
            
        user_id = patient.id
        
        # Get all patient data
        consultations = Consultation.query.filter_by(patient_id=user_id).all()
        medications = Medication.query.filter_by(patient_id=user_id).all()
        tickets = Ticket.query.filter_by(patient_id=user_id).all()
        
        # Export to CSV
        filepath = export_patient_data(patient, consultations, medications, tickets)
        
        # Return file path for download
        return jsonify({
            'ok': True,
            'message': 'Data exported successfully',
            'download_url': f'/api/patient/download/{os.path.basename(filepath)}'
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Export patient data failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@patient_export_bp.route('/download/<filename>', methods=['GET'])
def download_export(filename):
    """Download exported CSV file"""
    try:
        filepath = os.path.join('exports', filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            filepath,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"[ERROR] Download export failed: {e}")
        return jsonify({'error': str(e)}), 500
@patient_export_bp.route('/<int:patient_id>/consultations', methods=['GET'])
@jwt_required()
def get_patient_history(patient_id):
    """Doctor fetches patient's consultation history"""
    try:
        identity = get_jwt_identity()
        # Verify doctor is making the request
        if not identity or 'doctor:' not in str(identity):
            return jsonify({'error': 'Unauthorized. Only doctors can view patient history.'}), 403
            
        consultations = Consultation.query.filter_by(patient_id=patient_id).order_by(Consultation.created_at.desc()).all()
        
        return jsonify({
            'ok': True,
            'consultations': [c.to_dict() for c in consultations]
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get patient history failed: {e}")
        return jsonify({'error': str(e)}), 500
