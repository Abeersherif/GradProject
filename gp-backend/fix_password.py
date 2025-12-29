from app import app
from database import db
from models.user import User
from werkzeug.security import generate_password_hash

with app.app_context():
    user = User.query.get(1)
    if user:
        print(f"Found user: {user.email}")
        # Update password to be properly hashed
        user.password_hash = generate_password_hash("demo")
        db.session.commit()
        print("Password updated to 'demo' (hashed) successfully!")
    else:
        print("User not found!")
