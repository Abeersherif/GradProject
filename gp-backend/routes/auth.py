"""
Authentication routes for MedTwin
Handles user registration and login
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import Patient, Doctor
from database import db
import re
import json

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register/patient', methods=['POST'])
def register_patient():
    """Register a new patient"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('fullName') and not (data.get('firstName') and data.get('lastName')):
            return jsonify({'error': 'Full name or first name and last name are required'}), 400
        
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
            
        if not data.get('password'):
            return jsonify({'error': 'Password is required'}), 400
        
        # Validate email format
        if not is_valid_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if email exists in either table
        if Patient.query.filter_by(email=data['email']).first() or Doctor.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Parse date of birth
        from datetime import datetime as dt
        dob_obj = None
        if data.get('dob'):
            try:
                dob_obj = dt.strptime(data['dob'], '%Y-%m-%d').date()
            except:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Create medical data object
        medical_data = {}
        diseases = data.get('diseases', [])
        
        if 'diabetes' in diseases:
            medical_data['diabetes'] = {
                'type': data.get('diabetesType'),
                'lastHbA1c': data.get('diabetesLastHbA1c'),
                'currentMedications': data.get('diabetesCurrentMedications')
            }
        
        # Create new patient
        new_patient = Patient(
            full_name=f"{data.get('firstName', '')} {data.get('lastName', '')}".strip() or data.get('fullName', ''),
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role='patient',
            dob=dob_obj,
            gender=data.get('sex') or data.get('gender'),
            phone=data.get('phone'),
            height=data.get('height'),
            weight=data.get('weight'),
            blood_type=data.get('bloodType'),
            occupation=data.get('occupation'),
            marital_status=data.get('maritalStatus'),
            special_habits=data.get('specialHabits'),
            condition_category=','.join(diseases) if diseases else None,
            medical_data=json.dumps(medical_data) if medical_data else None
        )
        
        db.session.add(new_patient)
        db.session.commit()
        
        # Create access token (identity includes role to distinguish between tables)
        access_token = create_access_token(identity=f"patient:{new_patient.id}")
        
        return jsonify({
            'ok': True,
            'patientId': f'P-{new_patient.id}',
            'access_token': access_token,
            'user': new_patient.to_dict(),
            'message': 'Patient registered successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register/doctor', methods=['POST'])
def register_doctor():
    """Register a new doctor"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
            
        if not data.get('specialty'):
            return jsonify({'error': 'Specialty is required'}), 400

        # Check if email exists in either table
        if Patient.query.filter_by(email=data['email']).first() or Doctor.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Safely convert years_of_experience to int
        years = data.get('yearsExperience')
        try:
            years = int(years) if years and str(years).strip() else 0
        except:
            years = 0
            
        # Create new doctor
        new_doctor = Doctor(
            full_name=data.get('fullName') or f"{data.get('firstName', '')} {data.get('lastName', '')}".strip(),
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role='doctor',
            license_number=data.get('licenseNumber') or data.get('license'),
            specialty=data.get('specialty'),
            organization=data.get('hospital') or data.get('organization'),
            years_of_experience=years,
            bio=data.get('bio'),
            clinic_address=data.get('clinicAddress'),
            phone=data.get('phone')
        )
        
        db.session.add(new_doctor)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=f"doctor:{new_doctor.id}")
        
        return jsonify({
            'ok': True,
            'doctorId': f'D-{new_doctor.id}',
            'access_token': access_token,
            'user': new_doctor.to_dict(),
            'message': 'Doctor registered successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user - checks both tables"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # 1. Try Patient table
        user = Patient.query.filter_by(email=email).first()
        role = 'patient'
        
        # 2. Try Doctor table if not found
        if not user:
            user = Doctor.query.filter_by(email=email).first()
            role = 'doctor'
            
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create access token with role-prefixed identity
        access_token = create_access_token(identity=f"{role}:{user.id}")
        
        return jsonify({
            'ok': True,
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
