#!/usr/bin/env python3
"""
Update a training example with correct dimensions.

Usage:
    python update_training_example.py <image_path> <width_inches> <height_inches> <depth_inches>
"""

import sys
import os
import json
from package_scanner import PackageVolumeScanner

def main():
    if len(sys.argv) != 5:
        print("Usage: python update_training_example.py <image_path> <width_inches> <height_inches> <depth_inches>")
        print("\nExample:")
        print("  python update_training_example.py uploads/package.jpg 8.5 11 6")
        sys.exit(1)
    
    image_path = sys.argv[1]
    width_in = float(sys.argv[2])
    height_in = float(sys.argv[3])
    depth_in = float(sys.argv[4])
    
    # Convert to cm
    width_cm = width_in * 2.54
    height_cm = height_in * 2.54
    depth_cm = depth_in * 2.54
    
    scanner = PackageVolumeScanner()
    
    # Find and remove the old training example for this image
    scanner.training_data = [ex for ex in scanner.training_data if ex['image_path'] != image_path]
    
    # Add the corrected training example
    print(f"Updating training example:")
    print(f"  Image: {image_path}")
    print(f"  Dimensions: {width_in}\"W × {height_in}\"H × {depth_in}\"D ({width_cm}cm × {height_cm}cm × {depth_cm}cm)")
    print()
    
    if scanner.add_training_example(image_path, width_cm, height_cm, depth_cm):
        print(f"✅ Training example updated successfully!")
        print(f"   Total training examples: {len(scanner.training_data)}")
    else:
        print("❌ Failed to update training example. Check the logs for details.")
        sys.exit(1)

if __name__ == '__main__':
    main()

