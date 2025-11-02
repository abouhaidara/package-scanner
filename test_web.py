#!/usr/bin/env python3
"""
Simple web interface test script
"""

import requests
import os
import time

def test_web_interface():
    """Test the web interface."""
    print("🌐 Testing Web Interface")
    print("=" * 40)
    
    # Start the server in background
    print("🚀 Starting web server...")
    os.system("cd /Users/abouhaidara/package_scanner && python3 app.py &")
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:5000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test API scan endpoint
    try:
        with open("test_package.jpg", "rb") as f:
            files = {"file": f}
            response = requests.post("http://localhost:5000/api/scan", files=files, timeout=30)
        
        if response.status_code == 200:
            print("✅ API scan test passed")
            result = response.json()
            if result.get('success'):
                print(f"   Volume: {result['dimensions']['volume_liters']} liters")
                print(f"   Dimensions: {result['dimensions']['width_cm']} x {result['dimensions']['height_cm']} x {result['dimensions']['depth_cm']} cm")
            else:
                print(f"   Error: {result.get('error')}")
        else:
            print(f"❌ API scan failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ API scan error: {e}")
    
    print("\n📝 Web interface test completed!")
    print("   You can now open http://localhost:5000 in your browser")

if __name__ == "__main__":
    test_web_interface()
