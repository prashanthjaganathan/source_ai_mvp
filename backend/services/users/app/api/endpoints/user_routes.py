from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ...crud.user_crud import (
    get_user, get_users, create_user, update_user, delete_user,
    get_user_by_email, count_users
)
from ...config.database import get_db
from ..schemas.user import User, UserCreate, UserUpdate, UserResponse, UserListResponse

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    return create_user(db=db, user=user)

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

@router.get("/profile", response_model=UserResponse)
def read_current_user_profile(db: Session = Depends(get_db)):
    """Get current user profile (placeholder - implement auth later)"""
    # This is a placeholder endpoint for demonstration
    # In a real app, you would get the user from JWT token or session
    db_user = get_user(db, user_id=1)  # Placeholder
    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return db_user

@router.put("/profile", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update current user profile (placeholder - implement auth later)"""
    # This is a placeholder endpoint for demonstration
    # In a real app, you would get the user from JWT token or session
    user_id = 1  # Placeholder
    db_user = update_user(db, user_id=user_id, user_update=user_update)
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
