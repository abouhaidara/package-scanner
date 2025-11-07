#!/usr/bin/env python3
"""
Quick script to add the package with dimensions: 16"L × 10"W × 12"D

Usage:
    python add_this_package.py <image_path>
    
Example:
    python add_this_package.py uploads/package1.jpg
"""

import sys
import os
from package_scanner import PackageVolumeScanner

# Dimensions from user: 16 in L × 10 in W × 12 in D
LENGTH_IN = 16.0  # inches (this is the height)
WIDTH_IN = 10.0   # inches
DEPTH_IN = 12.0   # inches

def main():
    if len(sys.argv) != 2:
        print("Usage: python add_this_package.py <image_path>")
        print("\nExample:")
        print("  python add_this_package.py uploads/package1.jpg")
        print("\nOr add multiple images:")
        print("  for img in uploads/*.jpg; do python add_this_package.py \"$img\"; done")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found: {image_path}")
        sys.exit(1)
    
    print(f"Adding training example:")
    print(f"  Image: {image_path}")
    print(f"  Dimensions: {LENGTH_IN}\"L × {WIDTH_IN}\"W × {DEPTH_IN}\"D")
    print()
    
    scanner = PackageVolumeScanner()
    
    # Convert to cm
    length_cm = LENGTH_IN * 2.54
    width_cm = WIDTH_IN * 2.54
    depth_cm = DEPTH_IN * 2.54
    
    # Note: In the scanner, we use (width, height, depth)
    # User provided: Length (height) = 16", Width = 10", Depth = 12"
    if scanner.add_training_example(image_path, width_cm, length_cm, depth_cm):
        print(f"✅ Training example added successfully!")
        print(f"   Total training examples: {len(scanner.training_data)}")
    else:
        print("❌ Failed to add training example. Check the logs for details.")
        sys.exit(1)

if __name__ == '__main__':
    main()

