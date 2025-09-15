#!/usr/bin/env python3
"""
Test script to verify the registration API works correctly
"""

import requests
import json

def test_registration():
    """Test user registration with the exact data from the error"""
    print("🧪 Testing User Registration API")
    print("=" * 40)
    
    # Test data from the user's error message
    test_data = {
        "email": "yashasrn@gmail.com",
        "password": "password123",
        "full_name": "yashas",
        "username": "yashas"
    }
    
    try:
        print(f"📤 Sending registration request...")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            "http://localhost:8001/users/register",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            response_data = response.json()
            print(f"User created: {json.dumps(response_data, indent=2)}")
            
            # Verify the response has the expected fields
            required_fields = ['id', 'uid', 'name', 'email', 'incentives_earned', 'incentives_redeemed', 'incentives_available']
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"⚠️ Missing fields: {missing_fields}")
            else:
                print("✅ All required fields present")
                
            return True
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_login():
    """Test login with the created user"""
    print("\n🔐 Testing Login API")
    print("=" * 40)
    
    login_data = {
        "email": "yashasrn@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/users/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📥 Login Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            response_data = response.json()
            print(f"Login response: {json.dumps(response_data, indent=2)}")
            return True
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Registration & Login Test")
    print("=" * 50)
    
    # Test registration
    reg_success = test_registration()
    
    if reg_success:
        # Test login
        login_success = test_login()
        
        if login_success:
            print("\n🎉 All tests passed! Registration and login working correctly.")
            print("\n📝 Frontend should now work with:")
            print("   - Status code 201 (Created) for successful registration")
            print("   - User object with 'name' field (not 'full_name')")
            print("   - Incentives fields instead of total_earnings")
            return 0
        else:
            print("\n⚠️ Registration worked but login failed")
            return 1
    else:
        print("\n❌ Registration failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

