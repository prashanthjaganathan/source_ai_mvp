#!/usr/bin/env python3
"""
Test script to verify S3 configuration and setup
"""

import os
import sys
import asyncio
from app.core.s3_service import S3Service
from app.config.s3_config import S3Config

async def test_s3_config():
    """Test S3 configuration"""
    print("🔧 Testing S3 Configuration...")
    
    # Check configuration
    config_result = S3Config.validate_config()
    print(f"Configuration valid: {config_result['valid']}")
    print(f"Config: {config_result['config']}")
    
    if config_result['issues']:
        print("⚠️  Issues found:")
        for issue in config_result['issues']:
            print(f"  - {issue}")
    
    # Test S3 service initialization
    print("\n📦 Testing S3 Service...")
    try:
        s3_service = S3Service()
        await s3_service.initialize()
        print("✅ S3 Service initialized successfully!")
        
        # Test bucket access
        print(f"✅ Bucket: {s3_service.bucket_name}")
        print(f"✅ Region: {s3_service.region}")
        print(f"✅ Base URL: {s3_service.base_url}")
        
        await s3_service.cleanup()
        
    except Exception as e:
        print(f"❌ S3 Service initialization failed: {e}")
        print("\n💡 To fix this, you need to:")
        print("1. Set up AWS credentials:")
        print("   export AWS_ACCESS_KEY_ID=your_access_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("2. Or configure AWS CLI: aws configure")
        print("3. Or use IAM roles if running on EC2")
        print("4. Make sure the S3 bucket exists or has permissions to create it")

if __name__ == "__main__":
    asyncio.run(test_s3_config())

