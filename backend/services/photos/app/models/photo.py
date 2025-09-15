from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..config.database import Base

class Photo(Base):
    """Photo model matching database schema"""
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    filename = Column(String(255), nullable=False)
    original_key = Column(String(500), nullable=False)  # S3 (or storage) key
    file_size = Column(Integer, nullable=True)  # Size in bytes
    mime_type = Column(String(100), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)  # Reference to user who uploaded
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Backward-compat alias so legacy code reading .file_path doesn't explode:
    @property
    def file_path(self) -> str:
        return self.original_key
