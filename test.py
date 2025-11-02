#!/usr/bin/env python3
"""
Test script for Package Volume Scanner

This script tests the basic functionality of the package scanner.
"""

import os
import sys
import tempfile
import numpy as np
from PIL import Image
from package_scanner import PackageVolumeScanner


def create_test_image():
    """Create a simple test image with a rectangular shape."""
    # Create a simple test image with a rectangle
    width, height = 400, 300
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Draw a white rectangle (simulating a package)
    cv2 = __import__('cv2')
    cv2.rectangle(image, (50, 50), (350, 250), (255, 255, 255), -1)
    
    # Add some noise to make it more realistic
    noise = np.random.randint(0, 50, (height, width, 3), dtype=np.uint8)
    image = cv2.add(image, noise)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    cv2.imwrite(temp_file.name, image)
    temp_file.close()
    
    return temp_file.name


def test_scanner_initialization():
    """Test scanner initialization."""
    print("🧪 Testing scanner initialization...")
    try:
        scanner = PackageVolumeScanner()
        print("✅ Scanner initialized successfully")
        return scanner
    except Exception as e:
        print(f"❌ Scanner initialization failed: {e}")
        return None


def test_dimension_detection(scanner):
    """Test dimension detection."""
    print("🧪 Testing dimension detection...")
    
    # Create test image
    test_image_path = create_test_image()
    print(f"📷 Created test image: {test_image_path}")
    
    try:
        dimensions = scanner.detect_package_dimensions(test_image_path)
        print("✅ Dimension detection successful")
        print(f"   Width: {dimensions['width_cm']} cm")
        print(f"   Height: {dimensions['height_cm']} cm")
        print(f"   Depth: {dimensions['depth_cm']} cm")
        print(f"   Volume: {dimensions['volume_liters']} liters")
        
        # Clean up test image
        os.unlink(test_image_path)
        return True
        
    except Exception as e:
        print(f"❌ Dimension detection failed: {e}")
        # Clean up test image
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)
        return False


def test_cloud_configuration(scanner):
    """Test cloud storage configuration."""
    print("🧪 Testing cloud storage configuration...")
    
    if scanner.storage_client:
        print("✅ Google Cloud Storage configured")
        return True
    else:
        print("⚠️ Google Cloud Storage not configured (this is optional)")
        return True


def test_environment_variables():
    """Test environment variable loading."""
    print("🧪 Testing environment variables...")
    
    required_vars = ['UPLOAD_FOLDER']
    optional_vars = ['GOOGLE_CLOUD_PROJECT_ID', 'GOOGLE_CLOUD_BUCKET_NAME']
    
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️ {var}: Not set (using default)")
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"ℹ️ {var}: Not set (optional)")
    
    return all_good


def main():
    """Run all tests."""
    print("🚀 Package Volume Scanner Test Suite")
    print("=" * 50)
    
    # Test environment variables
    test_environment_variables()
    print()
    
    # Test scanner initialization
    scanner = test_scanner_initialization()
    if not scanner:
        print("❌ Cannot continue tests - scanner initialization failed")
        sys.exit(1)
    print()
    
    # Test cloud configuration
    test_cloud_configuration(scanner)
    print()
    
    # Test dimension detection
    success = test_dimension_detection(scanner)
    print()
    
    # Summary
    print("=" * 50)
    if success:
        print("🎉 All tests passed! The package scanner is ready to use.")
        print("\nNext steps:")
        print("1. Run the web app: python app.py")
        print("2. Or use CLI: python cli.py <image_path>")
        print("3. Or try examples: python example.py <image_path>")
    else:
        print("❌ Some tests failed. Please check the configuration.")
        sys.exit(1)


if __name__ == '__main__':
    main()
