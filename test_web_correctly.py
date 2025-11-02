#!/usr/bin/env python3
"""
Web Interface Test Script - Avoids "Method Not Allowed" errors

This script shows you the correct way to test the web interface
without getting HTTP method errors.
"""

import requests
import os
import sys

def test_web_interface(test_image_path=None):
    """Test the web interface correctly."""
    base_url = "http://127.0.0.1:5002"
    
    print("🌐 Testing Web Interface Correctly")
    print("=" * 50)
    
    # Test 1: Main page (GET request)
    print("1. Testing main page (GET request)...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Main page accessible")
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        else:
            print(f"❌ Main page error: {response.status_code}")
    except Exception as e:
        print(f"❌ Main page error: {e}")
    
    print()
    
    # Test 2: Health check (GET request)
    print("2. Testing health check (GET request)...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Scanner configured: {data.get('scanner_configured')}")
        else:
            print(f"❌ Health check error: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print()
    
    # Test 3: API scan (POST request) - This is where "Method Not Allowed" usually occurs
    print("3. Testing API scan (POST request)...")
    
    if test_image_path:
        if not os.path.exists(test_image_path):
            print(f"⚠️ Test image not found: {test_image_path}")
            print("   Please provide a valid package image path")
            return
    else:
        print("⚠️ No test image provided, skipping API test")
        print("   To test API, run: python3 test_web_correctly.py <path_to_package_image.jpg>")
        return
    
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/api/scan", files=files, timeout=30)
        
        if response.status_code == 200:
            print("✅ API scan successful")
            data = response.json()
            if data.get('success'):
                dims = data['dimensions']
                print(f"   Volume: {dims['volume_liters']:.3f} liters")
                print(f"   Dimensions: {dims['width_cm']:.1f} x {dims['height_cm']:.1f} x {dims['depth_cm']:.1f} cm")
            else:
                print(f"   Error: {data.get('error')}")
        else:
            print(f"❌ API scan error: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ API scan error: {e}")
    
    print()
    
    # Test 4: Show what NOT to do
    print("4. Testing what causes 'Method Not Allowed' errors...")
    try:
        # This will cause "Method Not Allowed" because we're using GET instead of POST
        response = requests.get(f"{base_url}/api/scan", timeout=10)
        print(f"❌ GET request to /api/scan: {response.status_code} - {response.reason}")
    except Exception as e:
        print(f"❌ GET request error: {e}")
    
    try:
        # This will also cause "Method Not Allowed" because we're using GET instead of POST
        response = requests.get(f"{base_url}/upload", timeout=10)
        print(f"❌ GET request to /upload: {response.status_code} - {response.reason}")
    except Exception as e:
        print(f"❌ GET request error: {e}")
    
    print()
    print("=" * 50)
    print("📝 Summary:")
    print("✅ Use GET requests for: /, /health")
    print("✅ Use POST requests for: /upload, /api/scan")
    print("❌ Don't use GET requests for: /upload, /api/scan")
    print()
    print("🌐 To use the web interface:")
    print("   1. Open browser to: http://127.0.0.1:5002")
    print("   2. Upload image via drag-and-drop")
    print("   3. View results automatically")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        # Test with provided image - run full test suite with the image
        image_path = sys.argv[1]
        if os.path.exists(image_path):
            test_web_interface(test_image_path=image_path)
        else:
            print(f"❌ Image not found: {image_path}")
    else:
        # Run test suite without image (will skip API scan test)
        test_web_interface()

if __name__ == '__main__':
    main()
