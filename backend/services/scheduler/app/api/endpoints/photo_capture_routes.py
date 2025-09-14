# /backend/services/scheduler/app/api/endpoints/photo_capture_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ...config.database import get_db
from ...models.schedule import Schedule
from ...models.capture_session import CaptureSession
from ...core.photo_capture_service import PhotoCaptureService
from ..schemas.photo_capture import PhotoCaptureRequest, PhotoCaptureResponse, CapturedPhotosResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
photo_capture_service = PhotoCaptureService()

@router.post("/capture", response_model=PhotoCaptureResponse)
async def trigger_manual_capture(
    capture_request: PhotoCaptureRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually trigger a photo capture for a user"""
    try:
        logger.info(f"Triggering manual capture for user: {capture_request.user_id}")
        
        # Check if user has an active schedule
        schedule = db.query(Schedule).filter(
            Schedule.user_id == capture_request.user_id,
            Schedule.is_active == True
        ).first()
        
        if not schedule:
            logger.warning(f"No active schedule found for user: {capture_request.user_id}")
            raise HTTPException(
                status_code=404,
                detail="No active schedule found for user"
            )
        
        logger.info(f"Found active schedule for user: {capture_request.user_id}, schedule_id: {schedule.id}")
        
        # Create capture session
        capture_session = CaptureSession(
            user_id=capture_request.user_id,
            schedule_id=schedule.id,
            triggered_at=datetime.utcnow(),
            status="pending"
        )
        db.add(capture_session)
        db.commit()
        db.refresh(capture_session)
        
        logger.info(f"Created capture session: {capture_session.id}")
        
        # Trigger photo capture in background
        background_tasks.add_task(
            photo_capture_service.capture_photo_for_user,
            capture_request.user_id,
            str(capture_session.id),
            "manual"
        )
        
        logger.info(f"Background task started for capture session: {capture_session.id}")
        
        return PhotoCaptureResponse(
            success=True,
            capture_session_id=str(capture_session.id),
            user_id=capture_request.user_id,
            message="Photo capture initiated"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in trigger_manual_capture: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/photos", response_model=CapturedPhotosResponse)
async def get_captured_photos(user_id: Optional[str] = None):
    """Get captured photos for a user or all users"""
    try:
        photos_info = await photo_capture_service.get_captured_photos(user_id)
        return CapturedPhotosResponse(**photos_info)
        
    except Exception as e:
        logger.error(f"Error getting captured photos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/photos/{user_id}")
async def get_user_captured_photos(user_id: str):
    """Get captured photos for a specific user"""
    try:
        photos_info = await photo_capture_service.get_captured_photos(user_id)
        return photos_info
        
    except Exception as e:
        logger.error(f"Error getting user captured photos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{user_id}")
async def get_user_capture_sessions(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get capture sessions for a user"""
    try:
        sessions = db.query(CaptureSession).filter(
            CaptureSession.user_id == user_id
        ).order_by(CaptureSession.triggered_at.desc()).limit(limit).all()
        
        return {
            "user_id": user_id,
            "total_sessions": len(sessions),
            "sessions": [
                {
                    "id": session.id,
                    "triggered_at": session.triggered_at,
                    "completed_at": session.completed_at,
                    "status": session.status,
                    "earnings_amount": session.earnings_amount,
                    "photo_id": session.photo_id,
                    "error_message": session.error_message
                }
                for session in sessions
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting capture sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))