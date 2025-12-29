from app import app, db
from models.user import User

with app.app_context():
    users = User.query.all()
    print("--- USERS ---")
    for u in users:
        print(f"ID: {u.id} | Name: {u.full_name} | Email: {u.email}")
