from app import app
from database import db
import os
from models.user import Patient, Doctor

with app.app_context():
    # Force drop all
    print("Dropping all tables...")
    db.drop_all()
    
    # Also delete the file for good measure
    db_path = 'instance/medtwin.db'
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Physical file deleted.")
        except:
            print("Could not delete physical file, but tables dropped.")
            
    print("Creating fresh tables for Patients and Doctors...")
    db.create_all()
    
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    
    for table in ['patients', 'doctors', 'consultations', 'tickets']:
        columns = inspector.get_columns(table)
        column_names = [col['name'] for col in columns]
        print(f"\nTable '{table}' columns: {', '.join(column_names)}")

print("\nDatabase split successful!")
