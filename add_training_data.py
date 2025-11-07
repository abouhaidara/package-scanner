#!/usr/bin/env python3
"""
Simple script to add training data (images with known dimensions).

Usage:
    python add_training_data.py <image_path> <width_inches> <height_inches> <depth_inches>

Example:
    python add_training_data.py package1.jpg 12.5 8.3 6.2
"""

import sys
import os
from package_scanner import PackageVolumeScanner

def main():
    if len(sys.argv) != 5:
        print("Usage: python add_training_data.py <image_path> <width_inches> <height_inches> <depth_inches>")
        print("\nExample:")
        print("  python add_training_data.py package1.jpg 12.5 8.3 6.2")
        sys.exit(1)
    
    image_path = sys.argv[1]
    width_in = float(sys.argv[2])
    height_in = float(sys.argv[3])
    depth_in = float(sys.argv[4])
    
    # Convert inches to cm
    width_cm = width_in * 2.54
    height_cm = height_in * 2.54
    depth_cm = depth_in * 2.54
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    print(f"Adding training example:")
    print(f"  Image: {image_path}")
    print(f"  Dimensions: {width_in}\" × {height_in}\" × {depth_in}\" ({width_cm}cm × {height_cm}cm × {depth_cm}cm)")
    print()
    
    scanner = PackageVolumeScanner()
    
    if scanner.add_training_example(image_path, width_cm, height_cm, depth_cm):
        print(f"✅ Training example added successfully!")
        print(f"   Total training examples: {len(scanner.training_data)}")
    else:
        print("❌ Failed to add training example. Check the logs for details.")
        sys.exit(1)

if __name__ == '__main__':
    main()

