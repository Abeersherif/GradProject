from app import app
from database import db
from models.user import User
import os

with app.app_context():
    # Check if user 1 exists
    user = User.query.get(1)
    if not user:
        print("Creating test user with ID=1...")
        test_user = User(
            id=1,
            full_name="Alex Henderson",
            email="alex@medtwin.com",
            password_hash="demo", # Not hashed for demo simplicity
            role="patient"
        )
        db.session.add(test_user)
        db.session.commit()
        print("Success!")
    else:
        print("Test user already exists.")
