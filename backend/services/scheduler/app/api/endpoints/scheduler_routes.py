# /backend/services/scheduler/app/api/endpoints/scheduler_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ...config.database import get_db
from ...models.schedule import Schedule
from ...models.user_settings import UserSettings
from ...core.scheduler import SchedulerService  # Fixed import
from ..schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse

router = APIRouter()

# Initialize scheduler service
scheduler_service = SchedulerService()

@router.post("/schedules/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_user_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db)
):
    """Create a new photo capture schedule for a user"""
    try:
        # Check if user exists (optional validation)
        # In a real implementation, you might want to verify the user exists
        
        # Create schedule record
        db_schedule = Schedule(
            user_id=schedule_data.user_id,
            frequency_hours=schedule_data.frequency_hours,
            next_capture_at=datetime.utcnow() + timedelta(hours=schedule_data.frequency_hours),
            notifications_enabled=schedule_data.notifications_enabled,
            silent_mode_enabled=schedule_data.silent_mode_enabled,
            is_active=True
        )
        
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        
        return ScheduleResponse(
            id=db_schedule.id,
            user_id=db_schedule.user_id,
            frequency_hours=db_schedule.frequency_hours,
            next_capture_at=db_schedule.next_capture_at,
            last_triggered_at=db_schedule.last_triggered_at,
            is_active=db_schedule.is_active,
            paused_at=db_schedule.paused_at,
            notifications_enabled=db_schedule.notifications_enabled,
            silent_mode_enabled=db_schedule.silent_mode_enabled,
            trigger_count=db_schedule.trigger_count,
            created_at=db_schedule.created_at,
            updated_at=db_schedule.updated_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating schedule: {str(e)}"
        )

@router.get("/schedules/", response_model=List[ScheduleResponse])
async def get_user_schedules(
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get schedules, optionally filtered by user_id"""
    try:
        query = db.query(Schedule)
        
        if user_id:
            query = query.filter(Schedule.user_id == user_id)
        
        schedules = query.offset(skip).limit(limit).all()
        
        return [
            ScheduleResponse(
                id=schedule.id,
                user_id=schedule.user_id,
                frequency_hours=schedule.frequency_hours,
                next_capture_at=schedule.next_capture_at,
                last_triggered_at=schedule.last_triggered_at,
                is_active=schedule.is_active,
                paused_at=schedule.paused_at,
                notifications_enabled=schedule.notifications_enabled,
                silent_mode_enabled=schedule.silent_mode_enabled,
                trigger_count=schedule.trigger_count,
                created_at=schedule.created_at,
                updated_at=schedule.updated_at
            )
            for schedule in schedules
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving schedules: {str(e)}"
        )

@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific schedule by ID"""
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        
        if not schedule:
            raise HTTPException(
                status_code=404,
                detail="Schedule not found"
            )
        
        return ScheduleResponse(
            id=schedule.id,
            user_id=schedule.user_id,
            frequency_hours=schedule.frequency_hours,
            notifications_enabled=schedule.notifications_enabled,
            silent_mode_enabled=schedule.silent_mode_enabled,
            is_active=schedule.is_active,
            created_at=schedule.created_at,
            updated_at=schedule.updated_at,
            last_triggered_at=schedule.last_triggered_at,
            trigger_count=schedule.trigger_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving schedule: {str(e)}"
        )

@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_update: ScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Update a schedule"""
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        
        if not schedule:
            raise HTTPException(
                status_code=404,
                detail="Schedule not found"
            )
        
        # Update fields
        update_data = schedule_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(schedule, field, value)
        
        schedule.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(schedule)
        
        return ScheduleResponse(
            id=schedule.id,
            user_id=schedule.user_id,
            frequency_hours=schedule.frequency_hours,
            notifications_enabled=schedule.notifications_enabled,
            silent_mode_enabled=schedule.silent_mode_enabled,
            is_active=schedule.is_active,
            created_at=schedule.created_at,
            updated_at=schedule.updated_at,
            last_triggered_at=schedule.last_triggered_at,
            trigger_count=schedule.trigger_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating schedule: {str(e)}"
        )

@router.post("/schedules/{schedule_id}/pause")
async def pause_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Pause a schedule"""
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        
        if not schedule:
            raise HTTPException(
                status_code=404,
                detail="Schedule not found"
            )
        
        schedule.is_active = False
        schedule.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Schedule paused successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error pausing schedule: {str(e)}"
        )

@router.post("/schedules/{schedule_id}/resume")
async def resume_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Resume a paused schedule"""
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        
        if not schedule:
            raise HTTPException(
                status_code=404,
                detail="Schedule not found"
            )
        
        schedule.is_active = True
        schedule.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Schedule resumed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error resuming schedule: {str(e)}"
        )

@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Delete a schedule"""
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        
        if not schedule:
            raise HTTPException(
                status_code=404,
                detail="Schedule not found"
            )
        
        db.delete(schedule)
        db.commit()
        
        return {"message": "Schedule deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting schedule: {str(e)}"
        )

@router.get("/status")
async def get_scheduler_status():
    """Get scheduler service status"""
    try:
        return {
            "is_running": scheduler_service.is_running,
            "service_status": "active" if scheduler_service.is_running else "inactive"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting scheduler status: {str(e)}"
        )