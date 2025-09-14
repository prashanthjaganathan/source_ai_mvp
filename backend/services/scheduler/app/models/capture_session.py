# /backend/services/scheduler/app/models/capture_session.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.sql import func
from ..config.database import Base

class CaptureSession(Base):
    """Photo capture session tracking"""
    __tablename__ = "capture_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    schedule_id = Column(Integer, nullable=True)
    triggered_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending, completed, failed, expired
    photo_id = Column(String(255), nullable=True)
    earnings_amount = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    device_info = Column(Text, nullable=True)  # JSON with device details
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())