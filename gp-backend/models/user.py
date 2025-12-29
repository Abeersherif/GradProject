"""
Models for MedTwin Patients and Doctors
Separated into two distinct tables
"""

from datetime import datetime
from database import db

class Patient(db.Model):
    __tablename__ = 'patients'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Account fields
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='patient')
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Biometrics
    dob = db.Column(db.Date)
    gender = db.Column(db.String(20))
    height = db.Column(db.Float)  # in cm
    weight = db.Column(db.Float)  # in kg
    blood_type = db.Column(db.String(10))
    occupation = db.Column(db.String(100))
    marital_status = db.Column(db.String(20))
    special_habits = db.Column(db.Text)
    
    # Medical fields
    condition_category = db.Column(db.String(50))  # 'diabetic', 'heart', etc.
    diabetes_type = db.Column(db.String(20))
    insulin_usage = db.Column(db.String(10))
    hba1c = db.Column(db.Float)
    last_glucose = db.Column(db.Float)
    endocrinologist = db.Column(db.String(200))
    
    cardiac_type = db.Column(db.String(100))
    cardiologist = db.Column(db.String(200))
    last_ecg_date = db.Column(db.Date)
    cardiac_meds = db.Column(db.Text)
    
    other_conditions = db.Column(db.Text)
    
    # Comprehensive medical data (stored as JSON string for Digital Twin)
    medical_data = db.Column(db.Text, nullable=True)
    
    # Relationships
    consultations = db.relationship('Consultation', backref='patient', lazy=True)
    tickets = db.relationship('Ticket', backref='patient', lazy=True)
    medications = db.relationship('Medication', backref='patient', lazy=True)
    
    def __repr__(self):
        return f'<Patient {self.email}>'
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'fullName': self.full_name,
            'firstName': self.full_name.split()[0] if self.full_name else "",
            'lastName': self.full_name.split()[-1] if self.full_name and len(self.full_name.split()) > 1 else "",
            'email': self.email,
            'role': 'patient',
            'phone': self.phone,
            'gender': self.gender,
            'dob': self.dob.isoformat() if self.dob else None,
            'height': self.height,
            'weight': self.weight,
            'conditionCategory': self.condition_category,
            'medicalData': json.loads(self.medical_data) if self.medical_data else {},
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_by_identity(identity):
        """Helper to get user from role:id string"""
        if not identity or ':' not in str(identity):
            return None
        try:
            role, user_id = str(identity).split(':')
            if role == 'patient':
                return Patient.query.get(int(user_id))
            elif role == 'doctor':
                return Doctor.query.get(int(user_id))
        except:
            return None
        return None

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Account fields
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='doctor')
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Professional fields
    license_number = db.Column(db.String(100), unique=True)
    specialty = db.Column(db.String(100))
    organization = db.Column(db.String(200))
    years_of_experience = db.Column(db.Integer)
    bio = db.Column(db.Text)
    clinic_address = db.Column(db.String(500))
    
    # Relationships
    tickets = db.relationship('Ticket', backref='doctor', lazy=True)
    
    def __repr__(self):
        return f'<Doctor {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'fullName': self.full_name,
            'firstName': self.full_name.split()[0] if self.full_name else "",
            'lastName': self.full_name.split()[-1] if self.full_name and len(self.full_name.split()) > 1 else "",
            'email': self.email,
            'role': 'doctor',
            'phone': self.phone,
            'licenseNumber': self.license_number,
            'specialty': self.specialty,
            'organization': self.organization,
            'yearsExperience': self.years_of_experience,
            'bio': self.bio,
            'clinicAddress': self.clinic_address,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def get_by_identity(identity):
        """Helper to get user from role:id string"""
        if not identity or ':' not in str(identity):
            return None
        try:
            role, user_id = str(identity).split(':')
            if role == 'patient':
                return Patient.query.get(int(user_id))
            elif role == 'doctor':
                return Doctor.query.get(int(user_id))
        except:
            return None
        return None

# For backward compatibility during migration
User = Patient
