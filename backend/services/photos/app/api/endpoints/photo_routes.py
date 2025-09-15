from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from ...crud.photo_crud import (
    get_photo, get_photos, create_photo, update_photo, delete_photo,
    count_photos, save_uploaded_file, get_image_dimensions, generate_photo_url
)
from ...config.database import get_db
from ..schemas.photo import Photo, PhotoCreate, PhotoUpdate, PhotoResponse, PhotoListResponse, PhotoUploadResponse

router = APIRouter()

@router.post("/upload", response_model=PhotoUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    user_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a new photo"""
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    # Validate file size (10MB limit)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=400,
            detail="File size too large. Maximum size is 10MB."
        )
    
    try:
        # Save file
        filename, file_path = save_uploaded_file(file)
        
        # Get image dimensions
        width, height = get_image_dimensions(file_path)
        
        # Create photo record
        photo_data = PhotoCreate(
            title=title,
            description=description,
            filename=filename,
            original_key=file_path,
            user_id=user_id
        )
        
        db_photo = create_photo(
            db=db,
            photo=photo_data,
            filename=filename,
            original_key=file_path,
            file_size=file_size,
            mime_type=file.content_type,
            width=width,
            height=height
        )
        
        # Generate response
        photo_url = generate_photo_url(db_photo)
        photo_response = PhotoResponse(
            id=db_photo.id,
            title=db_photo.title,
            description=db_photo.description,
            filename=db_photo.filename,
            url=photo_url,
            file_size=db_photo.file_size,
            mime_type=db_photo.mime_type,
            width=db_photo.width,
            height=db_photo.height,
            user_id=db_photo.user_id,
            created_at=db_photo.created_at,
            updated_at=db_photo.updated_at
        )
        
        return PhotoUploadResponse(
            message="Photo uploaded successfully",
            photo=photo_response
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading photo: {str(e)}"
        )

@router.get("/", response_model=PhotoListResponse)
def read_photos(
    skip: int = Query(0, ge=0, description="Number of photos to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of photos to return"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db)
):
    """Get list of photos with pagination"""
    photos = get_photos(db, skip=skip, limit=limit, user_id=user_id)
    total = count_photos(db, user_id=user_id)
    pages = (total + limit - 1) // limit
    
    # Convert to response format with URLs
    photo_responses = []
    for photo in photos:
        photo_url = generate_photo_url(photo)
        photo_response = PhotoResponse(
            id=photo.id,
            uid=photo.uid,
            title=photo.title,
            description=photo.description,
            filename=photo.filename,
            original_key=photo.original_key,
            url=photo_url,
            file_size=photo.file_size,
            mime_type=photo.mime_type,
            width=photo.width,
            height=photo.height,
            user_id=photo.user_id,
            created_at=photo.created_at,
            updated_at=photo.updated_at
        )
        photo_responses.append(photo_response)
    
    return PhotoListResponse(
        photos=photo_responses,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages
    )

@router.get("/{photo_id}", response_model=PhotoResponse)
def read_photo(photo_id: int, db: Session = Depends(get_db)):
    """Get photo by ID"""
    db_photo = get_photo(db, photo_id=photo_id)
    if db_photo is None:
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )
    
    photo_url = generate_photo_url(db_photo)
    return PhotoResponse(
        id=db_photo.id,
        uid=db_photo.uid,
        title=db_photo.title,
        description=db_photo.description,
        filename=db_photo.filename,
        original_key=db_photo.original_key,
        url=photo_url,
        file_size=db_photo.file_size,
        mime_type=db_photo.mime_type,
        width=db_photo.width,
        height=db_photo.height,
        user_id=db_photo.user_id,
        created_at=db_photo.created_at,
        updated_at=db_photo.updated_at
    )

@router.put("/{photo_id}", response_model=PhotoResponse)
def update_photo_metadata(
    photo_id: int,
    photo_update: PhotoUpdate,
    db: Session = Depends(get_db)
):
    """Update photo metadata"""
    db_photo = update_photo(db, photo_id=photo_id, photo_update=photo_update)
    if db_photo is None:
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )
    
    photo_url = generate_photo_url(db_photo)
    return PhotoResponse(
        id=db_photo.id,
        uid=db_photo.uid,
        title=db_photo.title,
        description=db_photo.description,
        filename=db_photo.filename,
        original_key=db_photo.original_key,
        url=photo_url,
        file_size=db_photo.file_size,
        mime_type=db_photo.mime_type,
        width=db_photo.width,
        height=db_photo.height,
        user_id=db_photo.user_id,
        created_at=db_photo.created_at,
        updated_at=db_photo.updated_at
    )

@router.delete("/{photo_id}")
def delete_photo_by_id(photo_id: int, db: Session = Depends(get_db)):
    """Delete photo by ID"""
    success = delete_photo(db, photo_id=photo_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )
    return {"message": "Photo deleted successfully"}
