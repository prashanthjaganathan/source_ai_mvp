# /backend/services/users/app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.sql import func
from ..config.database import Base

class User(Base):
    """Enhanced User model with profile and settings"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile Info
    bio = Column(Text, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    
    # Photo Capture Settings
    capture_frequency_hours = Column(Integer, default=1)  # Default 1 hour
    notifications_enabled = Column(Boolean, default=True)
    silent_mode_enabled = Column(Boolean, default=False)
    max_daily_captures = Column(Integer, default=10)
    
    # Earnings & Stats
    total_earnings = Column(Float, default=0.0)
    total_photos_captured = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    last_capture_date = Column(DateTime(timezone=True), nullable=True)
    
    # Account Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)