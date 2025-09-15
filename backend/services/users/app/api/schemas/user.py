# /backend/services/users/app/api/schemas/user.py
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from datetime import datetime
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    """Base user schema"""
    name: str
    email: EmailStr
    age: Optional[int] = None
    gender: Optional[str] = None

class UserCreate(BaseModel):
    """Schema for creating a new user - flexible field names"""
    email: EmailStr
    password: str
    age: Optional[int] = None
    gender: Optional[str] = None
    
    # Support multiple field names for name
    name: Optional[str] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @model_validator(mode='before')
    @classmethod
    def set_name_from_alternatives(cls, values):
        """Use name, full_name, or username as the display name"""
        if isinstance(values, dict):
            name = values.get('name')
            full_name = values.get('full_name')
            username = values.get('username')
            
            if name:
                values['name'] = name
            elif full_name:
                values['name'] = full_name
            elif username:
                values['name'] = username
            else:
                raise ValueError('Either name, full_name, or username must be provided')
        
        return values
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v is not None and (v < 13 or v > 120):
            raise ValueError('Age must be between 13 and 120')
        return v
    
    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v.lower() not in ['male', 'female', 'other', 'prefer_not_to_say']:
            raise ValueError('Gender must be one of: male, female, other, prefer_not_to_say')
        return v

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v is not None and (v < 13 or v > 120):
            raise ValueError('Age must be between 13 and 120')
        return v
    
    @field_validator('gender')
    @classmethod
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
    
    @field_validator('capture_frequency_hours')
    @classmethod
    def validate_frequency(cls, v):
        if v is not None and (v < 1 or v > 24):
            raise ValueError('Capture frequency must be between 1 and 24 hours')
        return v
    
    @field_validator('max_daily_captures')
    @classmethod
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
    uid: UUID
    age: Optional[int] = None
    gender: Optional[str] = None
    incentives_earned: Optional[float] = 0.0
    incentives_redeemed: Optional[float] = 0.0
    incentives_available: Optional[float] = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    """Schema for user response without sensitive data"""
    id: int
    uid: UUID
    name: str
    email: str
    age: Optional[int] = None
    gender: Optional[str] = None
    incentives_earned: Optional[float] = 0.0
    incentives_redeemed: Optional[float] = 0.0
    incentives_available: Optional[float] = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

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
    incentives_earned: float
    incentives_redeemed: float
    incentives_available: float
    rank: Optional[int] = None
    # Additional fields for Streamlit dashboard
    total_photos_captured: Optional[int] = 0
    total_earnings: Optional[float] = 0.0
    monthly_earnings: Optional[float] = 0.0
    active_schedules: Optional[int] = 0