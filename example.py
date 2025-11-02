#!/usr/bin/env python3
"""
Example usage of Package Volume Scanner

This script demonstrates how to use the PackageVolumeScanner class
programmatically.
"""

import os
import sys
from package_scanner import PackageVolumeScanner


def example_basic_usage():
    """Basic usage example."""
    print("📦 Basic Package Scanner Example")
    print("=" * 40)
    
    # Initialize scanner
    scanner = PackageVolumeScanner()
    
    # Example image path (you would replace this with a real image)
    image_path = "example_package.jpg"
    
    # Check if example image exists
    if not os.path.exists(image_path):
        print(f"❌ Example image '{image_path}' not found")
        print("Please provide a package image to test with")
        return
    
    try:
        # Process the package
        result = scanner.process_package(image_path)
        
        if result['success']:
            print("✅ Package processed successfully!")
            print(f"\n📏 Dimensions:")
            print(f"   Width:  {result['dimensions']['width_cm']} cm")
            print(f"   Height: {result['dimensions']['height_cm']} cm")
            print(f"   Depth:  {result['dimensions']['depth_cm']} cm")
            print(f"\n🧮 Volume: {result['dimensions']['volume_liters']} liters")
            
            if result.get('image_url'):
                print(f"\n☁️ Cloud URL: {result['image_url']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")


def example_dimensions_only():
    """Example showing how to get dimensions without cloud upload."""
    print("\n📏 Dimensions Only Example")
    print("=" * 40)
    
    scanner = PackageVolumeScanner()
    image_path = "example_package.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ Example image '{image_path}' not found")
        return
    
    try:
        # Get dimensions without cloud upload
        dimensions = scanner.detect_package_dimensions(image_path)
        
        print("📐 Package Dimensions:")
        for key, value in dimensions.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")


def example_cloud_upload():
    """Example showing cloud upload functionality."""
    print("\n☁️ Cloud Upload Example")
    print("=" * 40)
    
    scanner = PackageVolumeScanner()
    image_path = "example_package.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ Example image '{image_path}' not found")
        return
    
    if not scanner.storage_client:
        print("⚠️ Google Cloud Storage not configured")
        print("Set GOOGLE_CLOUD_PROJECT_ID and GOOGLE_CLOUD_BUCKET_NAME in .env")
        return
    
    try:
        # Upload to cloud storage
        cloud_filename = "example_package_upload.jpg"
        url = scanner.upload_to_cloud(image_path, cloud_filename)
        
        if url:
            print(f"✅ Upload successful: {url}")
        else:
            print("❌ Upload failed")
            
    except Exception as e:
        print(f"❌ Exception: {e}")


def main():
    """Run all examples."""
    print("🚀 Package Volume Scanner Examples")
    print("=" * 50)
    
    # Check if we have an example image
    if len(sys.argv) > 1:
        # Use provided image path
        global image_path
        image_path = sys.argv[1]
        print(f"Using image: {image_path}")
    else:
        print("No image provided. Using 'example_package.jpg'")
        print("Usage: python example.py <image_path>")
    
    # Run examples
    example_basic_usage()
    example_dimensions_only()
    example_cloud_upload()
    
    print("\n" + "=" * 50)
    print("🎉 Examples completed!")
    print("\nFor more information, see README.md")


if __name__ == '__main__':
    main()
