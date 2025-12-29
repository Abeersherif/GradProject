from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import text
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c:/Users/Administrator/Desktop/Agents/gp-backend/instance/medtwin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Minimal models for migration
class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    condition_category = db.Column(db.String(50))
    medical_data = db.Column(db.Text)

class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    specialty = db.Column(db.String(100))
    organization = db.Column(db.String(200))
    license_number = db.Column(db.String(100))

def migrate():
    with app.app_context():
        # Check if users table exists
        try:
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
            if not result.fetchone():
                print("No 'users' table found.")
                return
        except Exception as e:
            print(f"Error checking for users table: {e}")
            return

        print("Migrating users from legacy table...")
        
        users = db.session.execute(text("SELECT * FROM users")).fetchall()
        columns = db.session.execute(text("PRAGMA table_info(users)")).fetchall()
        col_map = {col[1]: i for i, col in enumerate(columns)}
        
        migrated_count = 0
        for u in users:
            email = u[col_map['email']]
            role = u[col_map['role']]
            
            if role == 'patient':
                if not Patient.query.filter_by(email=email).first():
                    new_user = Patient(
                        full_name=u[col_map['full_name']],
                        email=email,
                        password_hash=u[col_map['password_hash']],
                        role='patient',
                        phone=u[col_map['phone']],
                        gender=u[col_map['gender']],
                        condition_category=u[col_map['condition_category']],
                        medical_data=u[col_map['medical_data']]
                    )
                    db.session.add(new_user)
                    migrated_count += 1
                    print(f"Migrated Patient: {email}")
            
            elif role == 'doctor':
                if not Doctor.query.filter_by(email=email).first():
                    new_user = Doctor(
                        full_name=u[col_map['full_name']],
                        email=email,
                        password_hash=u[col_map['password_hash']],
                        role='doctor',
                        phone=u[col_map['phone']],
                        specialty=u[col_map['condition_category']] if 'condition_category' in col_map else 'General',
                        organization=u[col_map['medical_data']] if 'medical_data' in col_map else 'MedTwin',
                        license_number=f"LIC-{u[col_map['id']]}" # Dummy for migration
                    )
                    db.session.add(new_user)
                    migrated_count += 1
                    print(f"Migrated Doctor: {email}")
        
        db.session.commit()
        print(f"Migration complete. {migrated_count} users moved.")

if __name__ == "__main__":
    migrate()
