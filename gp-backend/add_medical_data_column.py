"""
Add medical_data column to users table
"""
from flask import Flask
from database import db
from models.user import User
import sqlite3
import os

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medtwin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # Get the database file path
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    # Connect directly to SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add the medical_data column as TEXT (JSON)
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN medical_data TEXT')
        conn.commit()
        print("✅ Successfully added medical_data column to users table!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️  Column medical_data already exists")
        elif "no such table" in str(e).lower():
            print("ℹ️  Table doesn't exist yet. Creating tables...")
            conn.close()
            db.create_all()
            print("✅ All tables created successfully!")
        else:
            print(f"❌ Error: {e}")
            conn.close()
            raise
    
    conn.close()
