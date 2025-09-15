#!/usr/bin/env python3
"""
Test script to verify the app is working correctly after sync changes.
Run this to check if all services are functioning properly.
"""

import requests
import time
import subprocess
import sys
import os
from pathlib import Path

def test_database_sync():
    """Test database-backend sync"""
    print("🔍 Testing database-backend sync...")
    try:
        result = subprocess.run(
            ["python", "check_sync.py"], 
            cwd="backend", 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print("✅ Database-backend sync: PASSED")
            return True
        else:
            print(f"❌ Database-backend sync: FAILED")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Database-backend sync: ERROR - {e}")
        return False

def start_service(service_name, port):
    """Start a service in the background"""
    print(f"🚀 Starting {service_name} on port {port}...")
    try:
        if service_name == "users":
            cmd = ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(port)]
            cwd = "backend/services/users"
        elif service_name == "photos":
            cmd = ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(port)]
            cwd = "backend/services/photos"
        else:
            return None
            
        process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)  # Give service time to start
        return process
    except Exception as e:
        print(f"❌ Failed to start {service_name}: {e}")
        return None

def test_service_health(service_name, port):
    """Test if a service is healthy"""
    print(f"🏥 Testing {service_name} health...")
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {service_name} health: PASSED - {data}")
            return True
        else:
            print(f"❌ {service_name} health: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {service_name} health: ERROR - {e}")
        return False

def test_api_endpoints(service_name, port):
    """Test API endpoints"""
    print(f"🌐 Testing {service_name} API endpoints...")
    try:
        # Test docs endpoint
        response = requests.get(f"http://localhost:{port}/docs", timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} docs: PASSED")
        else:
            print(f"❌ {service_name} docs: FAILED - Status {response.status_code}")
            return False
            
        # Test main endpoint
        if service_name == "users":
            endpoint = "/users/"
        elif service_name == "photos":
            endpoint = "/photos/"
        else:
            return False
            
        response = requests.get(f"http://localhost:{port}{endpoint}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {service_name} API: PASSED - {len(data)} items returned")
            return True
        else:
            print(f"❌ {service_name} API: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {service_name} API: ERROR - {e}")
        return False

def cleanup_processes():
    """Clean up any running processes"""
    print("🧹 Cleaning up processes...")
    try:
        subprocess.run(["pkill", "-f", "uvicorn"], capture_output=True)
        time.sleep(1)
    except:
        pass

def main():
    """Main test function"""
    print("🧪 Source AI MVP - App Testing Script")
    print("=" * 50)
    
    # Change to project root
    os.chdir(Path(__file__).parent)
    
    results = []
    
    # Test 1: Database sync
    results.append(test_database_sync())
    
    # Test 2: Start services
    users_process = start_service("users", 8001)
    photos_process = start_service("photos", 8002)
    
    if users_process and photos_process:
        try:
            # Test 3: Service health
            results.append(test_service_health("users", 8001))
            results.append(test_service_health("photos", 8002))
            
            # Test 4: API endpoints
            results.append(test_api_endpoints("users", 8001))
            results.append(test_api_endpoints("photos", 8002))
            
        finally:
            # Cleanup
            cleanup_processes()
            if users_process:
                users_process.terminate()
            if photos_process:
                photos_process.terminate()
    else:
        print("❌ Failed to start services")
        results.extend([False, False, False, False])
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your app is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
