"""
Database instance for MedTwin
Separates db from app to avoid circular imports
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
