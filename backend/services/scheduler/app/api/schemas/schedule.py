# /backend/services/scheduler/app/api/schemas/schedule.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ScheduleCreate(BaseModel):
    """Schema for creating a new schedule"""
    user_id: str = Field(..., description="User ID")
    frequency_hours: int = Field(..., ge=1, le=168, description="Frequency in hours (1-168)")
    notifications_enabled: bool = Field(True, description="Enable notifications")
    silent_mode_enabled: bool = Field(False, description="Enable silent mode")

class ScheduleUpdate(BaseModel):
    """Schema for updating a schedule"""
    frequency_hours: Optional[int] = Field(None, ge=1, le=168)
    notifications_enabled: Optional[bool] = None
    silent_mode_enabled: Optional[bool] = None

class ScheduleResponse(BaseModel):
    """Schema for schedule response"""
    id: int
    user_id: str
    frequency_hours: int
    next_capture_at: datetime
    last_triggered_at: Optional[datetime] = None
    is_active: bool
    paused_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True