from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Create SQLite database file in current directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./medtwin.db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# --- MODELS ---

class Patient(Base):
    """
    Core Patient Identity Table.
    Stores static demographics that apply effectively "forever" or change rarely.
    """
    __tablename__ = "patients"

    id = Column(String, primary_key=True, index=True)  # e.g., "DM_00000"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent_data = relationship("AgentData", back_populates="patient", cascade="all, delete-orphan")

class AgentData(Base):
    """
    The "Flexible Bucket" Table.
    Stores any data payload from any agent (Nutrition, Lab, Prediction, etc.)
    """
    __tablename__ = "agent_data"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"))
    
    agent_type = Column(String, index=True)  # e.g., "LabResults", "DietaryParams", "Prediction"
    data_payload = Column(JSON)              # The flexible JSON bucket
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="agent_data")

# --- UTILS ---

def init_db():
    """Create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
