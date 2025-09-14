# /backend/services/scheduler/app/api/schemas/photo_capture.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class PhotoCaptureRequest(BaseModel):
    """Schema for manual photo capture request"""
    user_id: str = Field(..., description="User ID to capture photo for")

class PhotoCaptureResponse(BaseModel):
    """Schema for photo capture response"""
    success: bool = Field(..., description="Whether capture was initiated successfully")
    capture_session_id: str = Field(..., description="Capture session ID")
    user_id: str = Field(..., description="User ID")
    message: str = Field(..., description="Response message")

class PhotoInfo(BaseModel):
    """Schema for photo information"""
    filename: str = Field(..., description="Photo filename")
    file_path: str = Field(..., description="Relative file path")
    absolute_path: str = Field(..., description="Absolute file path")
    size_bytes: int = Field(..., description="File size in bytes")
    modified: str = Field(..., description="Last modified timestamp")
    user_id: Optional[str] = Field(None, description="User ID")
    capture_session_id: Optional[str] = Field(None, description="Capture session ID")
    photo_info: Optional[Dict[str, Any]] = Field(None, description="Photo metadata")

class CapturedPhotosResponse(BaseModel):
    """Schema for captured photos response"""
    capture_directory: str = Field(..., description="Directory where photos are stored")
    total_photos: int = Field(..., description="Total number of photos")
    photos: List[PhotoInfo] = Field(..., description="List of photos")