from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="ANALYST")
    created_at = Column(DateTime, default=datetime.utcnow)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class Account(Base):
    __tablename__ = "accounts"
    
    account_id = Column(Integer, primary_key=True, index=True)
    attributes = Column(JSON, nullable=False) # Stores raw features dictionary
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    case = relationship("Case", back_populates="account", uselist=False)
    prediction = relationship("RiskPrediction", back_populates="account", uselist=False)
    shap_explanation = relationship("ShapExplanation", back_populates="account", uselist=False)
    events = relationship("InvestigationEvent", back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False) # e.g. UPI_INFLOW, CASH_OUTFLOW
    timestamp = Column(DateTime, default=datetime.utcnow)

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), unique=True, nullable=False)
    risk_score = Column(Float, nullable=False)
    tier = Column(String, nullable=False)
    status = Column(String, default="NEW") # NEW, TRIAGED, UNDER REVIEW, ESCALATED, CLOSED
    assigned_analyst = Column(String, default="Unassigned")
    created_at = Column(DateTime, default=datetime.utcnow)
    action = Column(String, nullable=False)
    notes = Column(JSON, default=list) # Stores notes as list of dicts: [{"timestamp", "analyst", "text"}]

    account = relationship("Account", back_populates="case")

class RiskPrediction(Base):
    __tablename__ = "risk_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), unique=True, nullable=False)
    risk_score = Column(Float, nullable=False)
    tier = Column(String, nullable=False)
    action = Column(String, nullable=False)
    exceeds_threshold = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="prediction")

class ShapExplanation(Base):
    __tablename__ = "shap_explanations"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), unique=True, nullable=False)
    features = Column(JSON, nullable=False) # Stores top contributing feature names list
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="shap_explanation")

class InvestigationEvent(Base):
    __tablename__ = "investigation_events"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event = Column(String, nullable=False) # e.g. Case Ingestion, Note Added, Status Updated
    detail = Column(Text, nullable=False)

    account = relationship("Account", back_populates="events")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    actor = Column(String, nullable=False)
    action = Column(String, nullable=False)
    case_id = Column(String, nullable=False)
    status = Column(String, nullable=False)

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    report_type = Column(String, nullable=False) # STR, PDF
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    filepath = Column(String, nullable=True)
