#!/usr/bin/env python3
"""
Test script for your own package images

Usage: python3 test_my_image.py <path_to_your_image>
"""

import sys
import os
from package_scanner import PackageVolumeScanner

def test_with_your_image(image_path):
    """Test the scanner with your own package image."""
    print("🧪 Testing Package Volume Scanner with Your Image")
    print("=" * 60)
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file '{image_path}' not found")
        return False
    
    # Check if it's an image file
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    file_ext = os.path.splitext(image_path)[1].lower()
    if file_ext not in valid_extensions:
        print(f"❌ Error: '{file_ext}' is not a supported image format")
        print(f"Supported formats: {', '.join(valid_extensions)}")
        return False
    
    print(f"📷 Processing image: {os.path.basename(image_path)}")
    print(f"📁 Full path: {image_path}")
    print()
    
    try:
        # Initialize scanner
        scanner = PackageVolumeScanner()
        
        # Process the image
        result = scanner.process_package(image_path)
        
        if result['success']:
            print("✅ Package processed successfully!")
            print()
            
            dimensions = result['dimensions']
            print("📏 DIMENSIONS:")
            print(f"   Width:  {dimensions['width_cm']:>6.2f} cm")
            print(f"   Height: {dimensions['height_cm']:>6.2f} cm")
            print(f"   Depth:  {dimensions['depth_cm']:>6.2f} cm")
            print()
            
            print("🧮 VOLUME:")
            print(f"   {dimensions['volume_cm3']:>8.2f} cm³")
            print(f"   {dimensions['volume_liters']:>8.3f} liters")
            print()
            
            if result.get('image_url'):
                print("☁️ CLOUD STORAGE:")
                print(f"   URL: {result['image_url']}")
            else:
                print("☁️ CLOUD STORAGE: Not configured")
            
            print()
            print("📊 SUMMARY:")
            print(f"   File: {os.path.basename(result['local_path'])}")
            print(f"   Processed: {result['timestamp']}")
            
            return True
        else:
            print(f"❌ Error processing package: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python3 test_my_image.py <path_to_your_image>")
        print()
        print("Examples:")
        print("  python3 test_my_image.py package.jpg")
        print("  python3 test_my_image.py /path/to/your/package.png")
        print("  python3 test_my_image.py ~/Desktop/box_image.jpeg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    success = test_with_your_image(image_path)
    
    print()
    print("=" * 60)
    if success:
        print("🎉 Test completed successfully!")
        print()
        print("Next steps:")
        print("1. Try the web interface: http://127.0.0.1:5002")
        print("2. Use CLI for batch processing: python3 cli.py <image> --verbose")
        print("3. Configure cloud storage in .env file for photo storage")
    else:
        print("❌ Test failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
