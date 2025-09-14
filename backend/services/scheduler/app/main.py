# /backend/services/scheduler/app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
import logging
from datetime import datetime, timedelta
import asyncio

from .api.endpoints import scheduler_routes, notification_routes, photo_capture_routes
from .core.scheduler import SchedulerService  # Fixed import
from .core.notification_service import NotificationService
from .config.database import get_db, engine, Base
from .models.schedule import Schedule
from .models.user_settings import UserSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Scheduler Service",
    description="Background photo capture scheduling and notification service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
scheduler_service = SchedulerService()
notification_service = NotificationService()

# Include routers
app.include_router(
    scheduler_routes.router,
    prefix="/scheduler",
    tags=["scheduler"]
)

app.include_router(
    notification_routes.router,
    prefix="/notifications",
    tags=["notifications"]
)

# Add photo capture routes
app.include_router(
    photo_capture_routes.router,
    prefix="/capture",
    tags=["photo-capture"]
)

@app.on_event("startup")
async def startup_event():
    """Initialize the scheduler service on startup"""
    logger.info("Starting up Enhanced Scheduler Service...")
    
    try:
        # Initialize services
        await scheduler_service.initialize()
        await notification_service.initialize()
        
        # Initialize photo capture service
        await photo_capture_routes.photo_capture_service.initialize()
        
        # Start background scheduler
        await scheduler_service.start_scheduler()
        
        logger.info("Enhanced Scheduler Service startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Enhanced Scheduler Service...")
    
    try:
        await scheduler_service.cleanup()
        await notification_service.cleanup()
        await photo_capture_routes.photo_capture_service.cleanup()
        
        logger.info("Enhanced Scheduler Service shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "service": "scheduler",
            "version": "1.0.0",
            "scheduler_running": scheduler_service.is_running,
            "features": [
                "user_integration",
                "photo_capture",
                "notifications",
                "background_scheduling"
            ]
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "service": "scheduler",
            "version": "1.0.0",
            "error": str(e)
        }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Enhanced Scheduler Service API",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "user_profile_integration",
            "photo_capture_scheduling",
            "notification_management",
            "background_task_processing",
            "real_camera_capture"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )