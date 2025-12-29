"""
Medical Ticket model for MedTwin
Handles doctor review of AI-generated consultations
"""

from datetime import datetime
from database import db

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultations.id'), nullable=False)
    
    # Medical ticket data (from Coordinator Agent)
    status = db.Column(db.String(20), default='pending_review')  # 'pending_review', 'approved', 'needs_revision'
    medical_ticket_data = db.Column(db.JSON)  # Complete ticket from Coordinator Agent
    
    # Doctor review
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    doctor_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<MedicalTicket {self.id} - Consultation {self.consultation_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'patientId': self.patient_id,
            'consultationId': self.consultation_id,
            'status': self.status,
            'medicalTicketData': self.medical_ticket_data,
            'doctorId': self.doctor_id,
            'doctorNotes': self.doctor_notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'reviewedAt': self.reviewed_at.isoformat() if self.reviewed_at else None
        }

