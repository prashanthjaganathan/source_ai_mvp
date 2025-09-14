# /backend/services/scheduler/app/api/schemas/notification.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class NotificationRequest(BaseModel):
    """Schema for sending notifications"""
    user_id: str = Field(..., description="User ID to send notification to")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional notification data")

class NotificationResponse(BaseModel):
    """Schema for notification response"""
    success: bool = Field(..., description="Whether notification was sent successfully")
    message: str = Field(..., description="Response message")
    user_id: str = Field(..., description="User ID")