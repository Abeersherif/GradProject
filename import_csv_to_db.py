"""
Script to Migrate CSV Data to SQLite Database
Run this once to populate medtwin.db
"""

import pandas as pd
from database import init_db, SessionLocal, Patient, AgentData
from datetime import datetime

def migrate_csv_to_sqlite():
    print("🚀 Starting Migration: CSV -> SQLite")
    
    # 1. Initialize Database Tables
    init_db()
    print("✅ Database tables created (medtwin.db)")
    
    # 2. Read CSV
    try:
        df = pd.read_csv('diabetes_dataset.csv')
        print(f"✅ Loaded {len(df)} patient records from CSV")
    except FileNotFoundError:
        print("❌ Error: diabetes_dataset.csv not found!")
        return

    # 3. Import Data
    db = SessionLocal()
    count = 0
    
    try:
        for index, row in df.iterrows():
            patient_id = f"DM_{index:05d}"
            
            # A. Create Patient Identity (if not exists)
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if not patient:
                patient = Patient(
                   id=patient_id,
                   created_at=datetime.utcnow()
                )
                db.add(patient)
            
            # B. Create Initial Medical Record (Legacy Data)
            # Store the ENTIRE row as a JSON payload
            # efficient: Clean text keys, handle NaN
            data_payload = row.to_dict()
            
            # Clean up keys (remove spaces, lowercase)
            # But keep original structure for compatibility
            
            agent_record = AgentData(
                patient_id=patient_id,
                agent_type="LegacyCSV",   # Label this as initial CSV import
                data_payload=data_payload,
                timestamp=datetime.utcnow()
            )
            db.add(agent_record)
            count += 1
            
        db.commit()
        print(f"🎉 Success! Migrated {count} patients into the database.")
        
    except Exception as e:
        print(f"❌ Migration Failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_csv_to_sqlite()
