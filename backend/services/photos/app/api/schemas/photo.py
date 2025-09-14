from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PhotoBase(BaseModel):
    """Base photo schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[int] = None

class PhotoCreate(PhotoBase):
    """Schema for creating a new photo"""
    pass

class PhotoUpdate(BaseModel):
    """Schema for updating photo metadata"""
    title: Optional[str] = None
    description: Optional[str] = None

class Photo(PhotoBase):
    """Schema for photo response"""
    id: int
    filename: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PhotoResponse(BaseModel):
    """Schema for photo response with URL"""
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    filename: str
    url: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class PhotoListResponse(BaseModel):
    """Schema for paginated photo list response"""
    photos: list[PhotoResponse]
    total: int
    page: int
    size: int
    pages: int

class PhotoUploadResponse(BaseModel):
    """Schema for photo upload response"""
    message: str
    photo: PhotoResponse
