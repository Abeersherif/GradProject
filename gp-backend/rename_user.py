from app import app, db
from models.user import User

with app.app_context():
    user = User.query.get(1)
    if user:
        user.full_name = "John Doe"
        db.session.commit()
        print("Updated User 1 to 'John Doe'")
