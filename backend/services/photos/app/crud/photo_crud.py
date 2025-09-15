from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import uuid
from PIL import Image

from ..models.photo import Photo as PhotoModel
from ..api.schemas.photo import PhotoCreate, PhotoUpdate

def get_photo(db: Session, photo_id: int) -> Optional[PhotoModel]:
    """Get photo by ID"""
    return db.query(PhotoModel).filter(PhotoModel.id == photo_id).first()

def get_photos(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[PhotoModel]:
    """Get list of photos with pagination and optional user filter"""
    query = db.query(PhotoModel)
    if user_id is not None:
        query = query.filter(PhotoModel.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_photo(db: Session, photo: PhotoCreate, filename: str, original_key: str, 
                file_size: int = None, mime_type: str = None, 
                width: int = None, height: int = None) -> PhotoModel:
    """Create a new photo record"""
    db_photo = PhotoModel(
        title=photo.title,
        description=photo.description,
        filename=filename,
        original_key=original_key,
        file_size=file_size,
        mime_type=mime_type,
        width=width,
        height=height,
        user_id=photo.user_id,
        created_at=datetime.utcnow()
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

def update_photo(db: Session, photo_id: int, photo_update: PhotoUpdate) -> Optional[PhotoModel]:
    """Update photo metadata"""
    db_photo = get_photo(db, photo_id)
    if not db_photo:
        return None
    
    update_data = photo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_photo, field, value)
    
    db_photo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_photo)
    return db_photo

def delete_photo(db: Session, photo_id: int) -> bool:
    """Delete a photo and its file"""
    db_photo = get_photo(db, photo_id)
    if not db_photo:
        return False
    
    # Delete the file from filesystem
    try:
        if os.path.exists(db_photo.original_key):
            os.remove(db_photo.original_key)
    except Exception as e:
        print(f"Error deleting file {db_photo.original_key}: {e}")
    
    db.delete(db_photo)
    db.commit()
    return True

def count_photos(db: Session, user_id: Optional[int] = None) -> int:
    """Count total number of photos"""
    query = db.query(PhotoModel)
    if user_id is not None:
        query = query.filter(PhotoModel.user_id == user_id)
    return query.count()

def save_uploaded_file(file, upload_dir: str = "uploads") -> tuple[str, str]:
    """Save uploaded file and return filename and file path"""
    # Create upload directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    return unique_filename, file_path

def get_image_dimensions(file_path: str) -> tuple[Optional[int], Optional[int]]:
    """Get image dimensions"""
    try:
        with Image.open(file_path) as img:
            return img.size  # Returns (width, height)
    except Exception as e:
        print(f"Error getting image dimensions: {e}")
        return None, None

def generate_photo_url(photo: PhotoModel, base_url: str = "http://localhost:8002") -> str:
    """Generate public URL for photo"""
    return f"{base_url}/uploads/{photo.filename}"
