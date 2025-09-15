#!/usr/bin/env python3
"""
Test script to verify user creation API works with the new schema
"""

import requests
import json
import time
import subprocess
import sys
import os

def start_service():
    """Start the users service"""
    print("🚀 Starting users service...")
    try:
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"],
            cwd="backend/services/users",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(5)  # Give service time to start
        return process
    except Exception as e:
        print(f"❌ Failed to start service: {e}")
        return None

def test_user_creation():
    """Test user creation with the new schema"""
    print("🧪 Testing user creation...")
    
    # Test data with your original format
    test_data = {
        "email": "yashasrn33@gmail.com",
        "password": "password123",  # Fixed password length
        "full_name": "yashas",
        "username": "yashas"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/users/register",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ User creation successful!")
            return True
        else:
            print("❌ User creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 User Creation API Test")
    print("=" * 40)
    
    # Start service
    process = start_service()
    if not process:
        return 1
    
    try:
        # Test user creation
        success = test_user_creation()
        
        if success:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print("\n⚠️ Tests failed")
            return 1
            
    finally:
        # Cleanup
        if process:
            process.terminate()
            process.wait()

if __name__ == "__main__":
    sys.exit(main())

