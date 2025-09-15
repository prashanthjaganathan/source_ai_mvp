# /backend/services/scheduler/app/models/schedule.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from ..config.database import Base

class Schedule(Base):
    """Photo capture schedule model"""
    __tablename__ = "photo_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    frequency_hours = Column(Integer, nullable=False)
    next_capture_at = Column(DateTime(timezone=True), nullable=False)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    paused_at = Column(DateTime(timezone=True), nullable=True)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    silent_mode_enabled = Column(Boolean, default=False, nullable=False)
    trigger_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())