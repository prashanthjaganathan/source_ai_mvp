# /backend/services/scheduler/app/config/s3_config.py
import os
from typing import Optional

class S3Config:
    """S3 configuration settings"""
    
    # S3 Bucket Configuration
    BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "source-ai-photos")
    REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # AWS Credentials
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN: Optional[str] = os.getenv("AWS_SESSION_TOKEN")
    
    # Storage Configuration
    USE_S3_STORAGE: bool = os.getenv("USE_S3_STORAGE", "true").lower() == "true"
    PHOTO_PREFIX: str = os.getenv("S3_PHOTO_PREFIX", "photos")
    
    # URL Configuration
    CLOUDFRONT_DOMAIN: Optional[str] = os.getenv("CLOUDFRONT_DOMAIN")
    CUSTOM_DOMAIN: Optional[str] = os.getenv("S3_CUSTOM_DOMAIN")
    
    @classmethod
    def get_base_url(cls) -> str:
        """Get the base URL for photo access"""
        if cls.CLOUDFRONT_DOMAIN:
            return f"https://{cls.CLOUDFRONT_DOMAIN}"
        elif cls.CUSTOM_DOMAIN:
            return f"https://{cls.CUSTOM_DOMAIN}"
        else:
            return f"https://{cls.BUCKET_NAME}.s3.{cls.REGION}.amazonaws.com"
    
    @classmethod
    def get_photo_url(cls, s3_key: str) -> str:
        """Get full URL for a photo"""
        return f"{cls.get_base_url()}/{s3_key}"
    
    @classmethod
    def validate_config(cls) -> dict:
        """Validate S3 configuration"""
        issues = []
        
        if cls.USE_S3_STORAGE:
            if not cls.BUCKET_NAME:
                issues.append("S3_BUCKET_NAME is required")
            
            if not cls.REGION:
                issues.append("AWS_REGION is required")
            
            # Credentials are optional (can use IAM roles)
            if not cls.AWS_ACCESS_KEY_ID and not cls.AWS_SECRET_ACCESS_KEY:
                issues.append("AWS credentials not provided (using default credentials)")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": {
                "bucket_name": cls.BUCKET_NAME,
                "region": cls.REGION,
                "use_s3": cls.USE_S3_STORAGE,
                "has_credentials": bool(cls.AWS_ACCESS_KEY_ID and cls.AWS_SECRET_ACCESS_KEY),
                "base_url": cls.get_base_url()
            }
        }
