# /backend/services/users/app/api/endpoints/user_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from ...crud.user_crud import (
    get_user, get_users, create_user, update_user, delete_user,
    get_user_by_email, count_users, authenticate_user, update_user_settings,
    update_user_stats, get_user_stats, get_leaderboard, get_active_users
)
from ...config.database import get_db  # Fixed import
from ...core.auth import create_access_token, get_current_active_user
from ..schemas.user import (
    User, UserCreate, UserUpdate, UserResponse, UserListResponse,
    UserLogin, Token, UserSettingsUpdate, UserStats
)
from ...models.user import User as UserModel

router = APIRouter()

# Authentication endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create user
    db_user = create_user(db=db, user=user)
    return db_user

@router.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# User profile endpoints
@router.get("/profile", response_model=UserResponse)
def get_current_user_profile(current_user: UserModel = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    db_user = update_user(db, current_user.id, user_update)
    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return db_user

@router.get("/profile/settings", response_model=dict)
def get_user_settings(current_user: UserModel = Depends(get_current_active_user)):
    """Get user capture settings"""
    return {
        "capture_frequency_hours": current_user.capture_frequency_hours,
        "notifications_enabled": current_user.notifications_enabled,
        "silent_mode_enabled": current_user.silent_mode_enabled,
        "max_daily_captures": current_user.max_daily_captures
    }

@router.put("/profile/settings", response_model=UserResponse)
def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user capture settings"""
    db_user = update_user_settings(db, current_user.id, settings_update)
    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return db_user

@router.get("/profile/stats", response_model=UserStats)
def get_user_statistics(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    stats = get_user_stats(db, current_user.id)
    if stats is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return UserStats(**stats)

# User management endpoints
@router.get("/", response_model=UserListResponse)
def read_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    db: Session = Depends(get_db)
):
    """Get list of users with pagination"""
    users = get_users(db, skip=skip, limit=limit)
    total = count_users(db)
    pages = (total + limit - 1) // limit
    
    return UserListResponse(
        users=users,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages
    )

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user_by_id(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user by ID"""
    db_user = update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return db_user

@router.delete("/{user_id}")
def delete_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Delete user by ID"""
    success = delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}

# Statistics and leaderboard endpoints
@router.get("/stats/overview")
def get_platform_stats(db: Session = Depends(get_db)):
    """Get platform statistics"""
    return {
        "total_users": count_users(db),
        "active_users": get_active_users(db),
        "total_photos_captured": db.query(UserModel).with_entities(
            db.func.sum(UserModel.total_photos_captured)
        ).scalar() or 0,
        "total_earnings": db.query(UserModel).with_entities(
            db.func.sum(UserModel.total_earnings)
        ).scalar() or 0.0
    }

@router.get("/leaderboard", response_model=List[UserResponse])
def get_leaderboard(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get leaderboard by total earnings"""
    return get_leaderboard(db, limit=limit)