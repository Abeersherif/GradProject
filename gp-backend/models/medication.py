"""
Medication model for MedTwin
Tracks patient medications
"""

from datetime import datetime
from database import db

class Medication(db.Model):
    __tablename__ = 'medications'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # Medication details
    name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)  # 'once daily', 'twice daily', etc.
    timing = db.Column(db.JSON)  # List of times ['08:00', '20:00']
    instructions = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.String(100))  # '30 days', 'ongoing', etc.
    active = db.Column(db.Boolean, default=True)
    
    # Google Calendar integration
    calendar_event_id = db.Column(db.String(200))  # Store Google Calendar event ID
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Medication {self.name} - {self.dosage}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'patientId': self.patient_id,
            'name': self.name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'timing': self.timing,
            'instructions': self.instructions,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'duration': self.duration,
            'active': self.active,
            'calendarEventId': self.calendar_event_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
