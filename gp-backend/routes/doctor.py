"""
Doctor Dashboard Routes
Handles doctor-side functionality including ticket review
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.consultation import Consultation
from models.ticket import Ticket
from models.user import Patient, Doctor, User
from agents import get_coordinator_agent
from utils.csv_export import export_patient_data
from datetime import datetime
from database import db
import os

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/queue', methods=['GET'])
@jwt_required()
def get_patient_queue():
    """Get pending patient tickets filtered by doctor specialty"""
    try:
        identity = get_jwt_identity()
        doctor = Doctor.get_by_identity(identity)
        
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
            
        specialty = doctor.specialty.lower() if doctor.specialty else ""
        
        # Mapping specialties to patient conditions
        specialty_map = {
            'pulmonology': ['copd'],
            'endocrinology': ['diabetes'],
            'cardiology': ['heartdisease', 'cardiac', 'cardiovascular']
        }
        
        target_conditions = specialty_map.get(specialty, [])
        
        # Get all consultations that are completed with care plans
        pending_consultations = Consultation.query.filter(
            Consultation.status == 'planned',
            Consultation.care_plan.isnot(None)
        ).order_by(Consultation.updated_at.desc()).all()
        
        queue = []
        coordinator_agent = get_coordinator_agent()
        
        for consultation in pending_consultations:
            patient = Patient.query.get(consultation.patient_id)
            if not patient:
                continue
                
            # FILTER LOGIC: Check if patient condition matches doctor specialty
            patient_conditions = patient.condition_category.lower() if patient.condition_category else ""
            
            # If the doctor has a specialty, filter. If not (general), show all or based on logic.
            # Here we assume we only show relevant ones if a specialty exists.
            if target_conditions:
                match = any(cond in patient_conditions for cond in target_conditions)
                if not match:
                    continue # Skip this patient as they don't match the doctor's specialty
            
            # Check if ticket already exists
            existing_ticket = Ticket.query.filter_by(consultation_id=consultation.id).first()
            
            if not existing_ticket:
                # Create medical ticket using Coordinator Agent
                consultation_dict = {
                    'id': consultation.id,
                    'patient_id': consultation.patient_id,
                    'created_at': consultation.created_at.isoformat() if consultation.created_at else None,
                    'analysis_result': consultation.analysis_result,
                    'care_plan': consultation.care_plan,
                    'collected_data': consultation.collected_data,
                    'conversation_history': consultation.conversation_history
                }
                
                medical_ticket = coordinator_agent.create_medical_ticket(consultation_dict)
                
                # Save to database
                ticket = Ticket(
                    consultation_id=consultation.id,
                    patient_id=consultation.patient_id,
                    status='pending_review',
                    medical_ticket_data=medical_ticket
                )
                db.session.add(ticket)
                db.session.commit()
                existing_ticket = ticket
            
            queue.append({
                'ticket_id': existing_ticket.id,
                'consultation_id': consultation.id,
                'patient': {
                    'id': patient.id,
                    'name': patient.full_name,
                    'email': patient.email,
                    'condition_category': patient.condition_category
                },
                'summary': existing_ticket.medical_ticket_data.get('summary', {}),
                'priority_score': existing_ticket.medical_ticket_data.get('priority_score', 3),
                'status': existing_ticket.status,
                'created_at': existing_ticket.created_at.isoformat() if existing_ticket.created_at else None
            })
        
        # Sort by priority
        queue.sort(key=lambda x: x['priority_score'])
        
        return jsonify({
            'ok': True,
            'queue': queue,
            'specialty_view': specialty,
            'total': len(queue)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get patient queue failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/ticket/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket_details(ticket_id):
    """Get complete ticket details for review"""
    try:
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        consultation = Consultation.query.get(ticket.consultation_id)
        patient = Patient.query.get(ticket.patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
            
        return jsonify({
            'ok': True,
            'ticket': {
                'id': ticket.id,
                'status': ticket.status,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                'medical_ticket': ticket.medical_ticket_data,
                'patient': {
                    'id': patient.id,
                    'name': patient.full_name,
                    'email': patient.email,
                    'phone': patient.phone,
                    'date_of_birth': patient.dob.isoformat() if patient.dob else None,
                    'gender': patient.gender,
                    'condition_category': patient.condition_category,
                    'medical_data': patient.medical_data
                },
                'consultation': consultation.to_dict() if consultation else None
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get ticket details failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/ticket/<int:ticket_id>/approve', methods=['POST'])
@jwt_required()
def approve_ticket(ticket_id):
    """Doctor approves or modifies the care plan"""
    try:
        identity = get_jwt_identity()
        doctor = Doctor.get_by_identity(identity)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
            
        doctor_id = doctor.id
        
        data = request.get_json()
        approved = data.get('approved', True)
        doctor_notes = data.get('doctor_notes', '')
        care_plan_modifications = data.get('care_plan_modifications', None)
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Update ticket
        ticket.status = 'approved' if approved else 'needs_revision'
        ticket.doctor_id = doctor_id
        ticket.doctor_notes = doctor_notes
        
        # Update medical ticket data
        if ticket.medical_ticket_data:
            # Create a copy to modify
            ticket_data = dict(ticket.medical_ticket_data)
            ticket_data['doctor_review'] = {
                'doctor_id': doctor_id,
                'doctor_name': doctor.full_name,
                'approved': approved,
                'review_notes': doctor_notes,
                'review_timestamp': str(datetime.utcnow()),
                'care_plan_modifications': care_plan_modifications
            }
            # Reassign to trigger update
            ticket.medical_ticket_data = ticket_data
        
        # Update consultation
        consultation = Consultation.query.get(ticket.consultation_id)
        if consultation:
            consultation.status = 'doctor_approved' if approved else 'needs_revision'
            
            # Apply care plan modifications if provided
            if care_plan_modifications and approved:
                consultation.care_plan = care_plan_modifications
        
        db.session.commit()
        
        return jsonify({
            'ok': True,
            'message': f'Ticket {"approved" if approved else "sent for revision"}',
            'ticket_id': ticket.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Approve ticket failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/patients', methods=['GET'])
@jwt_required()
def get_my_patients():
    """Get list of patients assigned to this doctor"""
    try:
        identity = get_jwt_identity()
        doctor = Doctor.get_by_identity(identity)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
            
        doctor_id = doctor.id
        
        # Find all tickets reviewed by this doctor
        approved_tickets = Ticket.query.filter_by(doctor_id=doctor_id, status='approved').all()
        patient_ids = list(set([t.patient_id for t in approved_tickets]))
        
        my_patients = []
        if patient_ids:
            patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
            for p in patients:
                # Calculate age
                age = "N/A"
                if p.dob:
                    try:
                        from datetime import date
                        if isinstance(p.dob, date):
                            age = (datetime.utcnow().date() - p.dob).days // 365
                        else:
                            # Try parsing string if it's a string
                            dob_dt = datetime.strptime(str(p.dob), '%Y-%m-%d').date()
                            age = (datetime.utcnow().date() - dob_dt).days // 365
                    except:
                        pass

                # Get last ticket for this patient/doctor pair
                last_ticket = Ticket.query.filter_by(patient_id=p.id, doctor_id=doctor_id).order_by(Ticket.created_at.desc()).first()

                # Parse medical data to be more readable
                raw_medical = p.medical_data
                parsed_medical = {}
                medical_summary = []
                
                # Add primary condition category first
                if p.condition_category:
                    medical_summary.append(f"Primary Conditions: {p.condition_category.upper()}")

                try:
                    if raw_medical:
                        import json
                        parsed_medical = json.loads(raw_medical)
                        for condition, details in parsed_medical.items():
                            if isinstance(details, dict):
                                detail_str = f"{condition.capitalize()} Details (" + ", ".join([f"{k}: {v}" for k, v in details.items() if v]) + ")"
                                medical_summary.append(detail_str)
                            else:
                                medical_summary.append(f"{condition.capitalize()}: {details}")
                except:
                    if raw_medical and str(raw_medical) not in medical_summary:
                        medical_summary.append(str(raw_medical))

                my_patients.append({
                    'id': p.id,
                    'name': p.full_name,
                    'email': p.email,
                    'phone': p.phone,
                    'gender': p.gender,
                    'age': age,
                    'blood_type': p.blood_type,
                    'condition': p.condition_category,
                    'medical_summary': medical_summary,
                    'last_visit': last_ticket.created_at.strftime('%Y-%m-%d') if last_ticket else 'N/A',
                    'status': 'Stable'
                })
        
        return jsonify({
            'ok': True,
            'patients': my_patients
        }), 200

    except Exception as e:
        print(f"[ERROR] Get my patients failed: {e}")
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/patient/<int:patient_id>/export', methods=['GET'])
# @jwt_required()
def export_patient_csv(patient_id):
    """Export complete patient data to CSV"""
    try:
        patient = User.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get all patient data
        from models.consultation import Consultation
        from models.medication import Medication
        from models.ticket import Ticket
        
        consultations = Consultation.query.filter_by(patient_id=patient_id).all()
        medications = Medication.query.filter_by(patient_id=patient_id).all()
        tickets = Ticket.query.filter_by(patient_id=patient_id).all()
        
        # Export to CSV
        filepath = export_patient_data(patient, consultations, medications, tickets)
        
        return jsonify({
            'ok': True,
            'message': 'Patient data exported successfully',
            'filepath': filepath,
            'filename': os.path.basename(filepath)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Export patient CSV failed: {e}")
        # import traceback
        # traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/dashboard', methods=['GET'])
# @jwt_required()
def get_doctor_dashboard():
    """Get doctor dashboard summary"""
    try:
        # Get real statistics
        doctor_id = 1
        
        total_pending = Ticket.query.filter_by(status='pending_review').count()
        today_approved = Ticket.query.filter_by(status='approved').count() # Simplified, ignoring date filter for now
        
        # Total patients assigned to THIS doctor
        my_patient_count = Ticket.query.filter_by(doctor_id=doctor_id, status='approved').with_entities(Ticket.patient_id).distinct().count()
        
        # Get recent tickets
        recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()
        
        tickets_list = []
        for ticket in recent_tickets:
            patient = User.query.get(ticket.patient_id)
            tickets_list.append({
                'id': ticket.id,
                'patient_name': patient.full_name if patient else 'Unknown',
                'status': ticket.status,
                'priority': ticket.medical_ticket_data.get('priority_score', 3) if ticket.medical_ticket_data else 3,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None
            })
        
        return jsonify({
            'ok': True,
            'statistics': {
                'pending_reviews': total_pending,
                'approved_today': today_approved,
                'total_patients': my_patient_count
            },
            'recent_tickets': tickets_list
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get doctor dashboard failed: {e}")
        return jsonify({'error': str(e)}), 500


import os
