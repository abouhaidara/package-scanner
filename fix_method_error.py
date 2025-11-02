#!/usr/bin/env python3
"""
Simple solution to avoid "Method Not Allowed" errors

This script provides the correct way to use the Package Volume Scanner
without getting HTTP method errors.
"""

import webbrowser
import time
import requests
import os
import sys

def open_web_interface():
    """Open the web interface correctly."""
    print("🌐 Opening Package Volume Scanner Web Interface")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:5002/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running on port 5002")
        else:
            print("❌ Server not responding properly")
            return False
    except Exception as e:
        print(f"❌ Server not running: {e}")
        print("Starting server...")
        
        # Try to start server
        import subprocess
        try:
            subprocess.Popen([
                "python3", "-c", 
                "import os; os.environ['PORT'] = '5002'; from app import app; app.run(host='127.0.0.1', port=5002, debug=False)"
            ], cwd="/Users/abouhaidara/package_scanner")
            print("⏳ Waiting for server to start...")
            time.sleep(3)
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    # Open browser to correct URL
    url = "http://127.0.0.1:5002"
    print(f"🌐 Opening browser to: {url}")
    
    try:
        webbrowser.open(url)
        print("✅ Browser opened successfully!")
        print()
        print("📝 Instructions:")
        print("1. Use the drag-and-drop area to upload your package image")
        print("2. Click 'Scan Package' to process the image")
        print("3. View the results with volume calculation")
        print()
        print("❌ DON'T type these URLs directly in browser:")
        print("   - http://127.0.0.1:5002/upload")
        print("   - http://127.0.0.1:5002/api/scan")
        print("   These will cause 'Method Not Allowed' errors!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"Please manually open: {url}")
        return False

def test_with_image(image_path):
    """Test with a specific image file."""
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return False
    
    print(f"🧪 Testing with image: {os.path.basename(image_path)}")
    print("=" * 40)
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post("http://127.0.0.1:5002/api/scan", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                dims = data['dimensions']
                print("✅ Success!")
                print(f"📏 Dimensions: {dims['width_cm']:.1f} x {dims['height_cm']:.1f} x {dims['depth_cm']:.1f} cm")
                print(f"🧮 Volume: {dims['volume_liters']:.3f} liters")
                return True
            else:
                print(f"❌ Processing failed: {data.get('error')}")
                return False
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Package Volume Scanner - Error-Free Usage")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Test with specific image
        image_path = sys.argv[1]
        test_with_image(image_path)
    else:
        # Open web interface
        open_web_interface()

if __name__ == '__main__':
    main()
