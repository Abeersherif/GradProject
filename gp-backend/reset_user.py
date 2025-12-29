from app import app
from database import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

with app.app_context():
    print("Resetting user alex@medtwin.com...")
    # Delete existing
    existing = User.query.filter_by(email="alex@medtwin.com").first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        print("Deleted old user.")
    
    # Create new
    pw_hash = generate_password_hash("demo")
    new_user = User(
        id=1,
        full_name="Alex Henderson",
        email="alex@medtwin.com",
        password_hash=pw_hash,
        role="patient"
    )
    db.session.add(new_user)
    db.session.commit()
    print("Created new user ID 1 with password 'demo'.")

    # Verify immediately
    u = User.query.filter_by(email="alex@medtwin.com").first()
    if u and check_password_hash(u.password_hash, "demo"):
        print("INTERNAL CHECKS: Password verification PASSED.")
    else:
        print("INTERNAL CHECKS: Password verification FAILED.")
