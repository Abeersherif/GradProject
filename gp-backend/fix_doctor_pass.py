from app import app
from database import db
from models.user import Doctor
from werkzeug.security import generate_password_hash

def reset_password():
    with app.app_context():
        email = "ahmedmohamed@gmail.com"
        new_password = "12345678"
        
        doc = Doctor.query.filter_by(email=email).first()
        if doc:
            print(f"Resetting password for {doc.full_name}...")
            doc.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print("Password reset successful!")
        else:
            print("Doctor not found.")

if __name__ == "__main__":
    reset_password()
