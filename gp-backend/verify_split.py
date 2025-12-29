from app import app
from database import db
from sqlalchemy import inspect
from models.user import Patient, Doctor

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {', '.join(tables)}")
    
    if 'patients' in tables:
        print("\n✅ 'patients' table exists")
        columns = [col['name'] for col in inspector.get_columns('patients')]
        print(f"Columns: {', '.join(columns)}")
        
    if 'doctors' in tables:
        print("\n✅ 'doctors' table exists")
        columns = [col['name'] for col in inspector.get_columns('doctors')]
        print(f"Columns: {', '.join(columns)}")

    if 'users' in tables:
        print("\n⚠️ 'users' table STILL exists (expected it to be gone)")
    else:
        print("\n✅ 'users' table successfully removed")
