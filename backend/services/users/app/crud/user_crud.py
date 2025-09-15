# /backend/services/users/app/crud/user_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from passlib.context import CryptContext
from typing import List, Optional
from datetime import datetime, timedelta

from ..models.user import User as UserModel
from ..api.schemas.user import UserCreate, UserUpdate, UserSettingsUpdate

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def get_user(db: Session, user_id: int) -> Optional[UserModel]:
    """Get user by ID"""
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    """Get user by email"""
    return db.query(UserModel).filter(UserModel.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
    """Get list of users with pagination"""
    return db.query(UserModel).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> UserModel:
    """Create a new user with default settings"""
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        name=user.name,
        email=user.email,
        age=user.age,
        gender=user.gender,
        hashed_password=hashed_password,
        # Default capture settings
        # Default incentives
        incentives_earned=0.0,
        incentives_redeemed=0.0,
        incentives_available=0.0,
        created_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserModel]:
    """Update user information"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_settings(db: Session, user_id: int, settings_update: UserSettingsUpdate) -> Optional[UserModel]:
    """Update user capture settings"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = settings_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_stats(db: Session, user_id: int, **stats) -> Optional[UserModel]:
    """Update user statistics"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    for field, value in stats.items():
        if hasattr(db_user, field):
            setattr(db_user, field, value)
    
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True

def authenticate_user(db: Session, email: str, password: str) -> Optional[UserModel]:
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    
    # Update last login (if field exists in model)
    # user.last_login = datetime.utcnow()
    # db.commit()
    
    return user

def get_user_stats(db: Session, user_id: int) -> Optional[dict]:
    """Get user statistics"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Calculate rank (based on total earnings)
    rank = db.query(UserModel).filter(
        UserModel.incentives_earned > (db_user.incentives_earned or 0.0)
    ).count() + 1
    
    # Get additional stats from other services
    total_photos_captured = 0
    active_schedules = 0
    monthly_earnings = 0.0
    
    try:
        import requests
        
        # Get photos count from scheduler service (where photos are actually stored)
        photos_response = requests.get(f"http://localhost:8003/capture/photos/{user_id}", timeout=5)
        if photos_response.status_code == 200:
            photos_data = photos_response.json()
            total_photos_captured = photos_data.get("total_photos", 0)
        
        # Get schedules from scheduler service
        schedules_response = requests.get(f"http://localhost:8003/scheduler/schedules/", 
                                        params={"user_id": str(user_id)}, timeout=5)
        if schedules_response.status_code == 200:
            schedules_data = schedules_response.json()
            active_schedules = len([s for s in schedules_data if s.get("is_active", False)])
            
    except Exception as e:
        # If external services are not available, use defaults
        pass
    
    # Calculate monthly earnings (placeholder - could be based on recent incentives)
    monthly_earnings = 0.45  # Fixed monthly earnings amount
    
    # Set total earnings to be the same as monthly earnings
    total_earnings = monthly_earnings
    
    # Update user's incentives_earned if it's less than calculated earnings
    if (db_user.incentives_earned or 0.0) < total_earnings:
        db_user.incentives_earned = total_earnings
        db_user.incentives_available = total_earnings - (db_user.incentives_redeemed or 0.0)
        db.commit()
    
    return {
        "incentives_earned": db_user.incentives_earned or 0.0,
        "incentives_redeemed": db_user.incentives_redeemed or 0.0,
        "incentives_available": db_user.incentives_available or 0.0,
        "rank": rank,
        # Fields expected by Streamlit app
        "total_photos_captured": total_photos_captured,
        "total_earnings": total_earnings,
        "monthly_earnings": monthly_earnings,
        "active_schedules": active_schedules
    }

def get_leaderboard(db: Session, limit: int = 10) -> List[UserModel]:
    """Get leaderboard by total earnings"""
    return db.query(UserModel).order_by(desc(UserModel.incentives_earned)).limit(limit).all()

def count_users(db: Session) -> int:
    """Count total number of users"""
    return db.query(UserModel).count()

def get_active_users(db: Session) -> int:
    """Count active users"""
    return db.query(UserModel).filter(UserModel.is_active == True).count()