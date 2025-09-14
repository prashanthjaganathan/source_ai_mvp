# /backend/services/users/app/api/schemas/user.py
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Base user schema"""
    name: str
    email: EmailStr
    bio: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 13 or v > 120):
            raise ValueError('Age must be between 13 and 120')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        if v is not None and v.lower() not in ['male', 'female', 'other', 'prefer_not_to_say']:
            raise ValueError('Gender must be one of: male, female, other, prefer_not_to_say')
        return v

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    profile_picture_url: Optional[str] = None
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 13 or v > 120):
            raise ValueError('Age must be between 13 and 120')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        if v is not None and v.lower() not in ['male', 'female', 'other', 'prefer_not_to_say']:
            raise ValueError('Gender must be one of: male, female, other, prefer_not_to_say')
        return v

class UserSettingsUpdate(BaseModel):
    """Schema for updating user capture settings"""
    capture_frequency_hours: Optional[int] = None
    notifications_enabled: Optional[bool] = None
    silent_mode_enabled: Optional[bool] = None
    max_daily_captures: Optional[int] = None
    
    @validator('capture_frequency_hours')
    def validate_frequency(cls, v):
        if v is not None and (v < 1 or v > 24):
            raise ValueError('Capture frequency must be between 1 and 24 hours')
        return v
    
    @validator('max_daily_captures')
    def validate_max_captures(cls, v):
        if v is not None and (v < 1 or v > 50):
            raise ValueError('Max daily captures must be between 1 and 50')
        return v

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class User(UserBase):
    """Schema for user response"""
    id: int
    profile_picture_url: Optional[str] = None
    capture_frequency_hours: int
    notifications_enabled: bool
    silent_mode_enabled: bool
    max_daily_captures: int
    total_earnings: float
    total_photos_captured: int
    streak_days: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    """Schema for user response without sensitive data"""
    id: int
    name: str
    email: str
    bio: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    profile_picture_url: Optional[str] = None
    capture_frequency_hours: int
    notifications_enabled: bool
    silent_mode_enabled: bool
    max_daily_captures: int
    total_earnings: float
    total_photos_captured: int
    streak_days: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

class UserListResponse(BaseModel):
    """Schema for paginated user list response"""
    users: list[UserResponse]
    total: int
    page: int
    size: int
    pages: int

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None

class UserStats(BaseModel):
    """Schema for user statistics"""
    total_earnings: float
    total_photos_captured: int
    streak_days: int
    average_daily_captures: float
    last_capture_date: Optional[datetime]
    rank: Optional[int] = None