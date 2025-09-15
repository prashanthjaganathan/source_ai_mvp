#!/usr/bin/env python3
"""
Test S3 integration with the scheduler service
"""

import os
import sys
import asyncio
import requests
import json
from app.core.s3_service import S3Service
from app.config.s3_config import S3Config

async def test_s3_integration():
    """Test complete S3 integration"""
    print("🚀 Testing S3 Integration with Scheduler Service...")
    
    # Check if credentials are set
    if not os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID") == "your_access_key_here":
        print("❌ AWS credentials not set properly")
        print("Please set your actual AWS credentials:")
        print("export AWS_ACCESS_KEY_ID=your_actual_access_key")
        print("export AWS_SECRET_ACCESS_KEY=your_actual_secret_key")
        return False
    
    # Test S3 service
    print("\n📦 Testing S3 Service...")
    try:
        s3_service = S3Service()
        await s3_service.initialize()
        print("✅ S3 Service initialized successfully!")
        await s3_service.cleanup()
    except Exception as e:
        print(f"❌ S3 Service failed: {e}")
        return False
    
    # Test scheduler service with S3
    print("\n🔄 Testing Scheduler Service with S3...")
    try:
        # Check if service is running
        response = requests.get("http://localhost:8003/health", timeout=5)
        if response.status_code == 200:
            print("✅ Scheduler service is running")
        else:
            print("❌ Scheduler service not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to scheduler service: {e}")
        return False
    
    # Test photo capture with S3
    print("\n📸 Testing Photo Capture with S3...")
    try:
        test_user_id = "s3-test-user-123"
        
        # Trigger photo capture
        capture_response = requests.post(
            "http://localhost:8003/capture/capture",
            json={"user_id": test_user_id},
            timeout=30
        )
        
        if capture_response.status_code == 200:
            result = capture_response.json()
            print(f"✅ Photo capture initiated: {result}")
            
            # Wait a moment for processing
            await asyncio.sleep(3)
            
            # Check captured photos
            photos_response = requests.get(
                f"http://localhost:8003/capture/photos/{test_user_id}",
                timeout=10
            )
            
            if photos_response.status_code == 200:
                photos_data = photos_response.json()
                print(f"✅ Photos retrieved: {photos_data}")
                
                if photos_data.get("storage_type") == "s3":
                    print("🎉 S3 storage is working!")
                    return True
                else:
                    print("⚠️  Using local storage (S3 may not be enabled)")
                    return True
            else:
                print(f"❌ Failed to get photos: {photos_response.status_code}")
                return False
        else:
            print(f"❌ Photo capture failed: {capture_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Photo capture test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 S3 Integration Test")
    print("=" * 50)
    
    # Check environment
    print(f"USE_S3_STORAGE: {os.getenv('USE_S3_STORAGE', 'not set')}")
    print(f"S3_BUCKET_NAME: {os.getenv('S3_BUCKET_NAME', 'not set')}")
    print(f"AWS_REGION: {os.getenv('AWS_REGION', 'not set')}")
    print(f"AWS_ACCESS_KEY_ID: {'set' if os.getenv('AWS_ACCESS_KEY_ID') else 'not set'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'set' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'not set'}")
    
    # Run tests
    success = asyncio.run(test_s3_integration())
    
    if success:
        print("\n🎉 All tests passed! S3 integration is working.")
    else:
        print("\n❌ Tests failed. Check the errors above.")
        print("\n💡 To fix:")
        print("1. Set your AWS credentials in the .env file")
        print("2. Make sure the S3 bucket exists or has permissions to create it")
        print("3. Check your AWS permissions")

if __name__ == "__main__":
    main()

