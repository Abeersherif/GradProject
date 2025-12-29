import os
import shutil
from app import app
from database import db
from sqlalchemy import inspect

# Path to the database
db_path = 'instance/medtwin.db'

print("Stopping any potential locks...")
# No easy way to kill other processes here, but we'll try to delete

if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"✅ Deleted {db_path}")
    except Exception as e:
        print(f"❌ Failed to delete {db_path}: {e}")
else:
    print(f"ℹ️ {db_path} already does not exist")

with app.app_context():
    print("\nCreating fresh tables with new schema...")
    db.create_all()
    
    # Verify columns in users table
    inspector = inspect(db.engine)
    columns = inspector.get_columns('users')
    column_names = [col['name'] for col in columns]
    print(f"\nUsers table columns: {', '.join(column_names)}")
    
    required_fields = ['years_of_experience', 'bio', 'clinic_address', 'medical_data']
    for field in required_fields:
        if field in column_names:
            print(f"✅ {field} column exists")
        else:
            print(f"❌ {field} column MISSSING!")

print("\nDatabase reset complete!")
