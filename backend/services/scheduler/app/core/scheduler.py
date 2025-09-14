# /backend/services/scheduler/app/core/scheduler.py
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..config.database import SessionLocal
from ..models.schedule import Schedule
from ..models.user_settings import UserSettings
from ..models.capture_session import CaptureSession
from .notification_service import NotificationService
from .photo_capture_service import PhotoCaptureService
from .user_service import UserService

logger = logging.getLogger(__name__)

class SchedulerService:
    """
    Enhanced Scheduler service with user integration
    """
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.photo_capture_service = PhotoCaptureService()
        self.user_service = UserService()
        self.is_running = False
        self._task = None
    
    async def initialize(self):
        """Initialize scheduler service"""
        logger.info("Initializing Enhanced Scheduler Service with User Integration...")
        
        # Initialize sub-services
        await self.notification_service.initialize()
        await self.photo_capture_service.initialize()
        
        logger.info("Enhanced Scheduler Service initialized")
    
    async def start_scheduler(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        logger.info("Starting Enhanced Scheduler...")
        
        # Start the background task
        self._task = asyncio.create_task(self._scheduler_loop())
        logger.info("Enhanced Scheduler started")
    
    async def stop_scheduler(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("Enhanced Scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                await self._check_and_trigger_captures()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)
    
    async def _check_and_trigger_captures(self):
        """Check schedules and trigger captures"""
        try:
            db = SessionLocal()
            try:
                # Get all active schedules
                schedules = db.query(Schedule).filter(Schedule.is_active == True).all()
                
                for schedule in schedules:
                    await self._process_schedule(schedule)
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error checking schedules: {e}")
    
    async def _process_schedule(self, schedule: Schedule):
        """Process a single schedule"""
        try:
            # Get user information
            user = await self.user_service.get_user(schedule.user_id)
            if not user:
                logger.warning(f"User {schedule.user_id} not found, skipping schedule")
                return
            
            # Check if it's time for capture
            if await self._should_trigger_capture(schedule, user):
                await self._trigger_photo_capture(schedule, user)
                
        except Exception as e:
            logger.error(f"Error processing schedule for user {schedule.user_id}: {e}")
    
    async def _should_trigger_capture(self, schedule: Schedule, user: Dict[str, Any]) -> bool:
        """Check if it's time to trigger a capture"""
        try:
            # Get user settings
            settings = await self.user_service.get_user_settings(schedule.user_id)
            if not settings:
                return False
            
            # Check frequency
            frequency_hours = settings.get("capture_frequency_hours", 1)
            last_capture = schedule.last_triggered_at
            
            if last_capture:
                time_since_last = datetime.utcnow() - last_capture
                if time_since_last < timedelta(hours=frequency_hours):
                    return False
            
            # Check daily limits
            max_daily = settings.get("max_daily_captures", 10)
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            db = SessionLocal()
            try:
                today_captures = db.query(CaptureSession).filter(
                    CaptureSession.user_id == schedule.user_id,
                    CaptureSession.created_at >= today_start
                ).count()
                
                if today_captures >= max_daily:
                    logger.info(f"User {schedule.user_id} has reached daily capture limit")
                    return False
                    
            finally:
                db.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking if should trigger capture: {e}")
            return False
    
    async def _trigger_photo_capture(self, schedule: Schedule, user: Dict[str, Any]):
        """Trigger photo capture for a user"""
        try:
            logger.info(f"Triggering photo capture for user {schedule.user_id}")
            
            # Create capture session
            capture_session = await self._create_capture_session(schedule.user_id)
            
            # Get user settings
            settings = await self.user_service.get_user_settings(schedule.user_id)
            notifications_enabled = settings.get("notifications_enabled", True)
            silent_mode = settings.get("silent_mode_enabled", False)
            
            # Send notification if enabled
            if notifications_enabled and not silent_mode:
                await self.notification_service.send_notification(
                    schedule.user_id,
                    "Photo Capture Time!",
                    "It's time to capture a photo and earn rewards!"
                )
            
            # Trigger photo capture
            result = await self.photo_capture_service.capture_photo_for_user(
                schedule.user_id,
                str(capture_session.id),
                "scheduled"
            )
            
            # Update schedule
            schedule.last_triggered_at = datetime.utcnow()
            schedule.trigger_count += 1
            
            # Update user stats
            if result.get("success"):
                await self.user_service.update_user_stats(
                    schedule.user_id,
                    total_photos_captured=user.get("total_photos_captured", 0) + 1,
                    total_earnings=user.get("total_earnings", 0.0) + result.get("earnings", 0.0),
                    last_capture_date=datetime.utcnow()
                )
            
            logger.info(f"Photo capture completed for user {schedule.user_id}: {result.get('success', False)}")
            
        except Exception as e:
            logger.error(f"Error triggering photo capture for user {schedule.user_id}: {e}")
    
    async def _create_capture_session(self, user_id: str) -> CaptureSession:
        """Create a new capture session"""
        db = SessionLocal()
        try:
            session = CaptureSession(
                user_id=user_id,
                status="pending",
                created_at=datetime.utcnow()
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return session
        finally:
            db.close()
    
    async def get_active_schedule_count(self) -> int:
        """Get count of active schedules"""
        try:
            db = SessionLocal()
            try:
                return db.query(Schedule).filter(Schedule.is_active == True).count()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting active schedule count: {e}")
            return 0
    
    async def get_last_capture_time(self) -> Optional[datetime]:
        """Get last capture time"""
        try:
            db = SessionLocal()
            try:
                last_session = db.query(CaptureSession).order_by(
                    CaptureSession.created_at.desc()
                ).first()
                return last_session.created_at if last_session else None
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting last capture time: {e}")
            return None
    
    async def cleanup(self):
        """Cleanup scheduler service"""
        await self.stop_scheduler()
        await self.notification_service.cleanup()
        await self.photo_capture_service.cleanup()
        await self.user_service.cleanup()
        logger.info("Enhanced Scheduler Service cleanup completed")