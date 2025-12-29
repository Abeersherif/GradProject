from app import app
from models.user import User

with app.app_context():
    user = User.query.get(1)
    if user:
        print(f"USER_EMAIL: {user.email}")
    else:
        print("USER_NOT_FOUND")
