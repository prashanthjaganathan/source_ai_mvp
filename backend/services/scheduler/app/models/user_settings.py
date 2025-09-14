# /backend/services/scheduler/app/models/user_settings.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from ..config.database import Base

class UserSettings(Base):
    """User settings for photo capture"""
    __tablename__ = "user_capture_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, unique=True, index=True)
    collection_frequency_hours = Column(Integer, nullable=False, default=24)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    silent_mode_enabled = Column(Boolean, default=False, nullable=False)
    device_tokens = Column(Text, nullable=True)  # JSON array of device tokens
    timezone = Column(String(50), nullable=True, default="UTC")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())