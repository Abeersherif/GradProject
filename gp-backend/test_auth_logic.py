from app import app
from models.user import Patient, Doctor
from werkzeug.security import check_password_hash

def test_login():
    with app.app_context():
        email = "ahmedmohamed@gmail.com"
        password = "12345678"
        
        # Check doctor
        doc = Doctor.query.filter_by(email=email).first()
        if doc:
            print(f"Found Doctor: {doc.full_name}")
            print(f"Hash in DB: {doc.password_hash}")
            result = check_password_hash(doc.password_hash, password)
            print(f"Password check: {result}")
        else:
            print("Doctor not found in DB.")

if __name__ == "__main__":
    test_login()
