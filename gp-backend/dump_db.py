from app import app, db
from models.user import User
from models.consultation import Consultation
from models.ticket import Ticket

with app.app_context():
    with open('db_dump.txt', 'w') as f:
        f.write("--- USERS ---\n")
        for u in User.query.all():
            f.write(f"ID: {u.id} | Name: {u.full_name}\n")
            
        f.write("\n--- CONSULTATIONS ---\n")
        for c in Consultation.query.all():
            f.write(f"ID: {c.id} | PatientID: {c.patient_id} | Status: {c.status} | HasPlan: {c.care_plan is not None}\n")
            
        f.write("\n--- TICKETS ---\n")
        for t in Ticket.query.all():
            f.write(f"ID: {t.id} | ConsultID: {t.consultation_id} | PatientID: {t.patient_id}\n")
