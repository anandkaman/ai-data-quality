from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, Text, Boolean
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatasetMetadata(Base):
    __tablename__ = "dataset_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    row_count = Column(Integer)
    column_count = Column(Integer)
    file_size_bytes = Column(Integer)
    schema_info = Column(JSON)
    status = Column(String)  # processing, completed, failed

class QualityAssessment(Base):
    __tablename__ = "quality_assessments"
    
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, index=True)
    assessment_timestamp = Column(DateTime, default=datetime.utcnow)
    completeness_score = Column(Float)
    consistency_score = Column(Float)
    accuracy_score = Column(Float)
    uniqueness_score = Column(Float)
    overall_score = Column(Float)
    quality_report = Column(JSON)

class AnomalyDetection(Base):
    __tablename__ = "anomaly_detections"
    
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, index=True)
    detection_timestamp = Column(DateTime, default=datetime.utcnow)
    model_used = Column(String)
    anomaly_count = Column(Integer)
    anomaly_indices = Column(JSON)
    anomaly_scores = Column(JSON)
    feature_contributions = Column(JSON)

class CleaningRecommendation(Base):
    __tablename__ = "cleaning_recommendations"
    
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, index=True)
    recommendation_timestamp = Column(DateTime, default=datetime.utcnow)
    strategies = Column(JSON)
    impact_analysis = Column(JSON)
    llm_reasoning = Column(Text)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Can link to User if needed
    name = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, index=True)
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
