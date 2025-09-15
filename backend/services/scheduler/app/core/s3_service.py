# /backend/services/scheduler/app/core/s3_service.py
import asyncio
import logging
import os
import uuid
import json
from typing import Dict, Any, Optional, Tuple
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime
import mimetypes

logger = logging.getLogger(__name__)

class S3Service:
    """
    S3 service for uploading and managing photos
    """
    
    def __init__(self):
        self.s3_client = None
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "source-ai-photos")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.base_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com"
        
    async def initialize(self):
        """Initialize S3 client"""
        try:
            logger.info("Initializing S3 Service...")
            
            # Initialize S3 client
            if self.aws_access_key_id and self.aws_secret_access_key:
                self.s3_client = boto3.client(
                    's3',
                    region_name=self.region,
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key
                )
                logger.info("S3 client initialized with credentials")
            else:
                # Use default credentials (IAM role, environment, etc.)
                self.s3_client = boto3.client('s3', region_name=self.region)
                logger.info("S3 client initialized with default credentials")
            
            # Test connection
            await self._test_connection()
            
            logger.info(f"S3 Service initialized - Bucket: {self.bucket_name}, Region: {self.region}")
            
        except Exception as e:
            logger.error(f"Error initializing S3 service: {e}")
            raise
    
    async def _test_connection(self):
        """Test S3 connection"""
        try:
            # Try to list objects in bucket (limited to 1)
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=1
            )
            logger.info("✅ S3 connection test successful")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                logger.warning(f"⚠️  S3 bucket '{self.bucket_name}' does not exist")
                await self._create_bucket()
            else:
                logger.error(f"S3 connection test failed: {e}")
                raise
        except NoCredentialsError:
            logger.error("❌ AWS credentials not found")
            raise
    
    async def _create_bucket(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            logger.info(f"Creating S3 bucket: {self.bucket_name}")
            
            if self.region == 'us-east-1':
                # us-east-1 doesn't need LocationConstraint
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            
            # Note: We're not setting public bucket policies due to AWS security restrictions
            # Photos will be accessed via pre-signed URLs instead
            logger.info("Bucket created successfully. Using pre-signed URLs for photo access.")
            
            logger.info(f"✅ S3 bucket '{self.bucket_name}' created successfully")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyOwnedByYou':
                logger.info(f"✅ S3 bucket '{self.bucket_name}' already exists and is owned by you")
            else:
                logger.error(f"Error creating S3 bucket: {e}")
                raise
    
    async def upload_photo(
        self, 
        photo_data: bytes, 
        user_id: str, 
        session_id: str,
        filename: str = None
    ) -> Dict[str, Any]:
        """
        Upload photo to S3
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_session_{session_id}.jpg"
            
            # Create S3 key
            s3_key = f"photos/{user_id}/{filename}"
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = "image/jpeg"
            
            # Upload to S3
            logger.info(f"Uploading photo to S3: {s3_key}")
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=photo_data,
                ContentType=content_type,
                Metadata={
                    'user_id': user_id,
                    'session_id': session_id,
                    'uploaded_at': datetime.now().isoformat(),
                    'source': 'scheduler_service'
                }
            )
            
            # Generate public URL
            photo_url = f"{self.base_url}/{s3_key}"
            
            result = {
                "success": True,
                "s3_key": s3_key,
                "photo_url": photo_url,
                "bucket": self.bucket_name,
                "filename": filename,
                "size_bytes": len(photo_data),
                "content_type": content_type,
                "uploaded_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Photo uploaded successfully: {photo_url}")
            return result
            
        except Exception as e:
            logger.error(f"Error uploading photo to S3: {e}")
            return {
                "success": False,
                "error": str(e),
                "s3_key": None,
                "photo_url": None
            }
    
    async def delete_photo(self, s3_key: str) -> bool:
        """
        Delete photo from S3
        """
        try:
            logger.info(f"Deleting photo from S3: {s3_key}")
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"✅ Photo deleted successfully: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting photo from S3: {e}")
            return False
    
    async def get_photo_url(self, s3_key: str) -> str:
        """
        Get public URL for photo
        """
        return f"{self.base_url}/{s3_key}"
    
    async def list_user_photos(self, user_id: str) -> Dict[str, Any]:
        """
        List all photos for a user
        """
        try:
            prefix = f"photos/{user_id}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            photos = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    photo_info = {
                        "s3_key": obj['Key'],
                        "filename": obj['Key'].split('/')[-1],
                        "size_bytes": obj['Size'],
                        "last_modified": obj['LastModified'].isoformat(),
                        "photo_url": f"{self.base_url}/{obj['Key']}"
                    }
                    photos.append(photo_info)
            
            return {
                "user_id": user_id,
                "total_photos": len(photos),
                "photos": photos,
                "bucket": self.bucket_name
            }
            
        except Exception as e:
            logger.error(f"Error listing user photos: {e}")
            return {
                "user_id": user_id,
                "total_photos": 0,
                "photos": [],
                "error": str(e)
            }
    
    async def get_photo_metadata(self, s3_key: str) -> Dict[str, Any]:
        """
        Get photo metadata from S3
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            return {
                "s3_key": s3_key,
                "size_bytes": response['ContentLength'],
                "content_type": response['ContentType'],
                "last_modified": response['LastModified'].isoformat(),
                "metadata": response.get('Metadata', {}),
                "photo_url": f"{self.base_url}/{s3_key}"
            }
            
        except Exception as e:
            logger.error(f"Error getting photo metadata: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup S3 service"""
        if self.s3_client:
            self.s3_client.close()
        logger.info("S3 Service cleanup completed")
