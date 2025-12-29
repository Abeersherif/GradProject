"""
Database migration script
Recreates tables with new schema
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db

print("Migrating database...")
print("-" * 50)

with app.app_context():
    # Drop all tables
    print("Dropping existing tables...")
    db.drop_all()
    
    # Create new tables with updated schema
    print("Creating new tables...")
    db.create_all()
    
    print("✓ Database migration complete!")
    print("-" * 50)
