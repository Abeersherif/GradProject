"""
Consultation model for MedTwin
Tracks patient consultations with AI agents
"""

from datetime import datetime
from database import db

class Consultation(db.Model):
    __tablename__ = 'consultations'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # Consultation data
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'cancelled'
    conversation_history = db.Column(db.JSON)  # Store chat messages
    collected_data = db.Column(db.JSON)  # Store collected symptoms/data
    analysis_result = db.Column(db.JSON)  # Store AI analysis
    treatment_plan = db.Column(db.JSON)  # Store treatment plan
    care_plan = db.Column(db.JSON)  # Store care plan (same as treatment_plan)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Consultation {self.id} - Patient {self.patient_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'patientId': self.patient_id,
            'status': self.status,
            'conversationHistory': self.conversation_history,
            'collectedData': self.collected_data,
            'analysisResult': self.analysis_result,
            'treatmentPlan': self.treatment_plan,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None
        }
