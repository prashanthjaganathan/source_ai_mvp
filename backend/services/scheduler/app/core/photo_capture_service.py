# /backend/services/scheduler/app/core/photo_capture_service.py
import asyncio
import logging
import os
import uuid
from typing import Dict, Any, Optional, Tuple
import httpx
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
from sqlalchemy.orm import Session
from ..config.database import SessionLocal
from ..models.capture_session import CaptureSession
from .mac_camera_capture import MacCameraCapture

logger = logging.getLogger(__name__)

class PhotoCaptureService:
    """
    Photo capture service with real Mac camera integration
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.capture_dir = "captured_photos"
        self.camera_capture = MacCameraCapture()
        self.setup_capture_directory()
        
    def setup_capture_directory(self):
        """Create directory for storing captured photos"""
        os.makedirs(self.capture_dir, exist_ok=True)
        logger.info(f"Photo capture directory: {os.path.abspath(self.capture_dir)}")
        
    async def initialize(self):
        """Initialize photo capture service"""
        logger.info("Initializing Photo Capture Service with Real Mac Camera...")
        logger.info(f"Photos will be stored in: {os.path.abspath(self.capture_dir)}")
        
        # Check camera availability
        camera_available = await self.camera_capture.check_camera_availability()
        if camera_available:
            logger.info("✅ Mac camera is available")
        else:
            logger.warning("⚠️  Mac camera may not be available")
        
        logger.info("Photo Capture Service initialized")
    
    async def capture_photo_for_user(
        self, 
        user_id: str, 
        capture_session_id: str,
        trigger_type: str = "scheduled"
    ) -> Dict[str, Any]:
        """
        Capture a REAL photo using the Mac's camera
        """
        try:
            logger.info(f"Capturing REAL photo for user {user_id} (session: {capture_session_id})")
            
            # Generate file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_session_{capture_session_id}.jpg"
            user_dir = os.path.join(self.capture_dir, user_id)
            os.makedirs(user_dir, exist_ok=True)
            photo_path = os.path.join(user_dir, filename)
            
            # Try to capture with real camera first
            camera_success, camera_error = await self.camera_capture.capture_photo(photo_path)
            
            if not camera_success:
                logger.warning(f"Camera capture failed: {camera_error}")
                logger.info("Falling back to generated photo...")
                
                # Fallback: create a photo with camera error info
                photo_data, photo_info = await self.create_fallback_photo(user_id, capture_session_id, camera_error)
                
                with open(photo_path, 'wb') as f:
                    f.write(photo_data)
                
                logger.info(f"Fallback photo saved: {photo_path}")
            else:
                logger.info(f"✅ Real camera photo captured: {photo_path}")
            
            # Get photo information
            photo_info = await self.get_photo_info(photo_path)
            
            # Update capture session
            await self.update_capture_session_status(
                capture_session_id, "captured", {
                    "photo_path": photo_path,
                    "trigger_type": trigger_type,
                    "photo_info": photo_info,
                    "camera_captured": camera_success,
                    "camera_error": camera_error if not camera_success else None
                }
            )
            
            # Process the photo
            result = await self.process_captured_photo(
                user_id, capture_session_id, photo_path, photo_info
            )
            
            result["camera_captured"] = camera_success
            if not camera_success:
                result["camera_error"] = camera_error
            
            return result
            
        except Exception as e:
            logger.error(f"Error capturing photo for user {user_id}: {e}")
            await self.update_capture_session_status(
                capture_session_id, "failed", {"error": str(e)}
            )
            return {"success": False, "error": str(e)}
    
    async def create_fallback_photo(self, user_id: str, capture_session_id: str, camera_error: str) -> Tuple[bytes, Dict[str, Any]]:
        """Create a fallback photo when camera capture fails"""
        try:
            # Create an image with error information
            img = Image.new('RGB', (800, 600), color='lightcoral')  # Light red background for errors
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
                small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Add error information to the image
            text_lines = [
                f"User ID: {user_id}",
                f"Session ID: {capture_session_id}",
                f"Capture Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Status: CAMERA CAPTURE FAILED",
                f"Error: {camera_error[:50]}..." if len(camera_error) > 50 else f"Error: {camera_error}",
                f"Fallback: Generated Photo"
            ]
            
            y_position = 50
            for i, line in enumerate(text_lines):
                current_font = font if i < 4 else small_font
                draw.text((50, y_position), line, fill='white', font=current_font)
                y_position += 40
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            photo_data = img_bytes.getvalue()
            
            # Get photo info
            photo_info = {
                "width": img.width,
                "height": img.height,
                "format": "JPEG",
                "size_bytes": len(photo_data),
                "generated_at": datetime.now().isoformat(),
                "fallback": True,
                "camera_error": camera_error
            }
            
            logger.info(f"Created fallback photo: {photo_info['width']}x{photo_info['height']}")
            return photo_data, photo_info
            
        except Exception as e:
            logger.error(f"Error creating fallback photo: {e}")
            # Ultimate fallback
            img = Image.new('RGB', (400, 300), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            return img_bytes.getvalue(), {"width": 400, "height": 300, "format": "JPEG", "fallback": True}
    
    async def get_photo_info(self, photo_path: str) -> Dict[str, Any]:
        """Get information about the captured photo"""
        try:
            with Image.open(photo_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "size_bytes": os.path.getsize(photo_path),
                    "captured_at": datetime.now().isoformat(),
                    "mode": img.mode
                }
        except Exception as e:
            logger.error(f"Error getting photo info: {e}")
            return {
                "size_bytes": os.path.getsize(photo_path) if os.path.exists(photo_path) else 0,
                "captured_at": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def process_captured_photo(
        self, 
        user_id: str, 
        capture_session_id: str,
        photo_path: str,
        photo_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process the captured photo"""
        try:
            logger.info(f"Processing captured photo for user {user_id}")
            
            # Simulate photo validation
            validation_result = await self.validate_photo(photo_path, user_id)
            
            if validation_result["valid"]:
                # Simulate upload
                upload_result = await self.upload_to_photos_service(
                    user_id, capture_session_id, photo_path, photo_info
                )
                
                if upload_result.get("success"):
                    # Process earnings
                    await self.process_earnings(user_id, upload_result)
                    
                    # Update session as completed
                    await self.update_capture_session_status(
                        capture_session_id, "completed", {
                            "photo_path": photo_path,
                            "validation_result": validation_result,
                            "upload_result": upload_result,
                            "earnings": 0.05
                        }
                    )
                    
                    return {
                        "success": True,
                        "photo_path": photo_path,
                        "photo_id": upload_result.get("photo_id"),
                        "earnings": 0.05,
                        "validation": validation_result
                    }
                else:
                    # Upload failed
                    await self.update_capture_session_status(
                        capture_session_id, "upload_failed", {
                            "photo_path": photo_path,
                            "validation_result": validation_result,
                            "upload_error": upload_result.get("error")
                        }
                    )
                    
                    return {
                        "success": False,
                        "error": "Upload failed",
                        "photo_path": photo_path,
                        "validation": validation_result
                    }
            else:
                # Photo validation failed
                await self.update_capture_session_status(
                    capture_session_id, "validation_failed", {
                        "photo_path": photo_path,
                        "validation_result": validation_result
                    }
                )
                
                return {
                    "success": False,
                    "error": "Photo validation failed",
                    "photo_path": photo_path,
                    "validation": validation_result
                }
                
        except Exception as e:
            logger.error(f"Error processing captured photo: {e}")
            return {"success": False, "error": str(e)}
    
    async def validate_photo(self, photo_path: str, user_id: str) -> Dict[str, Any]:
        """Validate the captured photo"""
        try:
            if not os.path.exists(photo_path):
                return {
                    "valid": False,
                    "error": "Photo file not found",
                    "validated_at": datetime.now().isoformat()
                }
            
            # Check file size
            file_size = os.path.getsize(photo_path)
            if file_size < 1000:  # Less than 1KB
                return {
                    "valid": False,
                    "error": "Photo file too small",
                    "file_size": file_size,
                    "validated_at": datetime.now().isoformat()
                }
            
            # Try to open the image
            try:
                with Image.open(photo_path) as img:
                    # Basic validation
                    is_valid = True
                    validation_notes = []
                    
                    # Check dimensions
                    if img.width < 100 or img.height < 100:
                        is_valid = False
                        validation_notes.append("Image too small")
                    
                    # Check if it's a real image
                    img.verify()
                    
                    return {
                        "valid": is_valid,
                        "image_size": f"{img.width}x{img.height}",
                        "file_size": file_size,
                        "validation_notes": validation_notes,
                        "validated_at": datetime.now().isoformat()
                    }
                    
            except Exception as img_error:
                return {
                    "valid": False,
                    "error": f"Invalid image file: {str(img_error)}",
                    "file_size": file_size,
                    "validated_at": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error validating photo: {e}")
            return {
                "valid": False,
                "error": str(e),
                "validated_at": datetime.now().isoformat()
            }
    
    async def upload_to_photos_service(
        self, 
        user_id: str, 
        capture_session_id: str,
        photo_path: str,
        photo_info: Dict[str, Any]
    ):
        """Simulate upload to photos service"""
        try:
            logger.info(f"Simulating upload to photos service for user {user_id}")
            
            # Simulate successful upload
            photo_id = f"photo_{uuid.uuid4().hex[:8]}"
            
            return {
                "success": True,
                "photo_id": photo_id,
                "url": f"http://localhost:8002/uploads/{user_id}/{photo_id}.jpg",
                "simulated": True
            }
                
        except Exception as e:
            logger.error(f"Error uploading to photos service: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_capture_session_status(
        self, 
        capture_session_id: str, 
        status: str, 
        data: Dict[str, Any]
    ):
        """Update capture session status in database"""
        try:
            db = SessionLocal()
            try:
                session = db.query(CaptureSession).filter(
                    CaptureSession.id == int(capture_session_id)
                ).first()
                
                if session:
                    session.status = status
                    session.updated_at = datetime.utcnow()
                    
                    if status == "completed":
                        session.completed_at = datetime.utcnow()
                        session.earnings_amount = data.get("earnings", 0.0)
                        session.photo_id = data.get("photo_id")
                    elif status in ["failed", "validation_failed", "upload_failed"]:
                        session.error_message = data.get("error", "Unknown error")
                    
                    db.commit()
                    logger.info(f"Updated capture session {capture_session_id} status to {status}")
                else:
                    logger.warning(f"Capture session {capture_session_id} not found")
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error updating capture session status: {e}")
    
    async def process_earnings(self, user_id: str, upload_response: Dict[str, Any]):
        """Process earnings for valid photo upload"""
        try:
            if upload_response.get("success"):
                logger.info(f"Processing $0.05 earnings for user {user_id}")
                # In real implementation, this would update the users service
                
        except Exception as e:
            logger.error(f"Error processing earnings: {e}")
    
    async def get_captured_photos(self, user_id: str = None) -> Dict[str, Any]:
        """Get information about captured photos"""
        try:
            photos_info = []
            
            if user_id:
                user_dir = os.path.join(self.capture_dir, user_id)
                if os.path.exists(user_dir):
                    for filename in os.listdir(user_dir):
                        if filename.endswith('.jpg'):
                            file_path = os.path.join(user_dir, filename)
                            
                            photo_info = {
                                "filename": filename,
                                "file_path": file_path,
                                "absolute_path": os.path.abspath(file_path),
                                "size_bytes": os.path.getsize(file_path),
                                "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                            }
                            
                            photos_info.append(photo_info)
            else:
                # Get all photos from all users
                if os.path.exists(self.capture_dir):
                    for user_folder in os.listdir(self.capture_dir):
                        user_path = os.path.join(self.capture_dir, user_folder)
                        if os.path.isdir(user_path):
                            user_photos = await self.get_captured_photos(user_folder)
                            photos_info.extend(user_photos.get("photos", []))
            
            return {
                "capture_directory": os.path.abspath(self.capture_dir),
                "total_photos": len(photos_info),
                "photos": photos_info
            }
            
        except Exception as e:
            logger.error(f"Error getting captured photos: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup photo capture service"""
        await self.http_client.aclose()
        logger.info("Photo Capture Service cleanup completed")