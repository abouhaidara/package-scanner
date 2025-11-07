#!/usr/bin/env python3
"""
Add multiple training examples at once.

Usage:
    python add_multiple_training.py
    
    Then provide image paths one by one, or edit this script to add them directly.
"""

import os
import sys
from package_scanner import PackageVolumeScanner

# Dimensions: 16"L × 10"W × 12"D
LENGTH_IN = 16.0
WIDTH_IN = 10.0
DEPTH_IN = 12.0

def add_example(scanner, image_path):
    """Add a training example."""
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return False
    
    print(f"\n📦 Processing: {os.path.basename(image_path)}")
    
    # Convert to cm
    width_cm = WIDTH_IN * 2.54
    height_cm = LENGTH_IN * 2.54  # Length is height
    depth_cm = DEPTH_IN * 2.54
    
    if scanner.add_training_example(image_path, width_cm, height_cm, depth_cm):
        print(f"  ✅ Added successfully!")
        return True
    else:
        print(f"  ❌ Failed to add")
        return False

def main():
    scanner = PackageVolumeScanner()
    
    # Get image paths from command line or use default
    if len(sys.argv) > 1:
        image_paths = sys.argv[1:]
    else:
        # Look for images in uploads folder
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            image_paths = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
                import glob
                image_paths.extend(glob.glob(os.path.join(uploads_dir, ext)))
        else:
            print("Usage: python add_multiple_training.py <image1> <image2> ...")
            print("\nOr place images in 'uploads/' folder and run without arguments")
            return
    
    if not image_paths:
        print("No images found. Please provide image paths:")
        print("  python add_multiple_training.py <image1> <image2> ...")
        return
    
    print(f"Adding {len(image_paths)} training examples...")
    print(f"Dimensions: {LENGTH_IN}\"L × {WIDTH_IN}\"W × {DEPTH_IN}\"D")
    print("=" * 60)
    
    success_count = 0
    for image_path in image_paths:
        if add_example(scanner, image_path):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Successfully added {success_count}/{len(image_paths)} examples")
    print(f"📊 Total training examples: {len(scanner.training_data)}")

if __name__ == '__main__':
    main()

