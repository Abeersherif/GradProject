"""
Check database status
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models.user import User
from models.consultation import Consultation
from models.ticket import Ticket

with app.app_context():
    print("\n" + "="*60)
    print("DATABASE STATUS CHECK")
    print("="*60 + "\n")
    
    # Check users
    users = User.query.all()
    print(f"Total Users: {len(users)}")
    for user in users:
        print(f"  - {user.full_name} ({user.email}) - Role: {user.role}")
    print()
    
    # Check consultations
    consultations = Consultation.query.all()
    print(f"Total Consultations: {len(consultations)}")
    for c in consultations:
        print(f"  - ID: {c.id}, Patient: {c.patient_id}, Status: {c.status}")
        print(f"    Has care_plan: {c.care_plan is not None}")
        print(f"    Has analysis: {c.analysis_result is not None}")
    print()
    
    # Check tickets
    tickets = Ticket.query.all()
    print(f"Total Tickets: {len(tickets)}")
    for t in tickets:
        print(f"  - ID: {t.id}, Patient: {t.patient_id}, Consultation: {t.consultation_id}, Status: {t.status}")
    print()
    
    print("="*60)
