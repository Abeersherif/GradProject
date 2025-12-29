from app import app, db
from models.user import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if user 1 exists
    user = User.query.get(1)
    if not user:
        print("Restoring User 1...")
        user = User(
            id=1,
            full_name="Restored Patient",
            email="restored@example.com",
            password_hash=generate_password_hash("password123"),
            role="patient",
            condition_category="COPD"
        )
        db.session.add(user)
        db.session.commit()
        print("User 1 restored successfully.")
    else:
        print("User 1 already exists.")
