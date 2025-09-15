# /backend/services/users/app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..config.database import Base

class User(Base):
    """User model matching database schema"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    
    # Basic Info
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile Info (only fields that exist in DB)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    
    # Incentives (matching DB schema)
    incentives_earned = Column(Float, default=0.0)
    incentives_redeemed = Column(Float, default=0.0)
    incentives_available = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Computed property to preserve existing code paths that used total_earnings
    @property
    def total_earnings(self) -> float:
        return self.incentives_earned or 0.0