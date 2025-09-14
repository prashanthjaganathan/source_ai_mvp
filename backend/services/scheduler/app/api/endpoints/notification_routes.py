# /backend/services/scheduler/app/api/endpoints/notification_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...config.database import get_db
from ...models.capture_session import CaptureSession
from ..schemas.notification import NotificationRequest, NotificationResponse

router = APIRouter()

@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    notification_data: NotificationRequest,
    db: Session = Depends(get_db)
):
    """Send a notification to a user"""
    try:
        # This would integrate with your notification service
        # For now, we'll just log the notification
        print(f"Sending notification to user {notification_data.user_id}: {notification_data.message}")
        
        return NotificationResponse(
            success=True,
            message="Notification sent successfully",
            user_id=notification_data.user_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{user_id}")
async def get_user_notification_sessions(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get notification sessions for a user"""
    sessions = db.query(CaptureSession).filter(
        CaptureSession.user_id == user_id
    ).all()
    
    return {"sessions": sessions}