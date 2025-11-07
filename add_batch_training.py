#!/usr/bin/env python3
"""
Batch script to add multiple training examples at once.

Usage:
    python add_batch_training.py
    
    Then provide image paths and dimensions interactively, or
    edit this script to add your images directly.
"""

import os
from package_scanner import PackageVolumeScanner

def add_training_example(scanner, image_path, width_in, height_in, depth_in):
    """Add a single training example."""
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return False
    
    width_cm = width_in * 2.54
    height_cm = height_in * 2.54
    depth_cm = depth_in * 2.54
    
    print(f"\nAdding: {os.path.basename(image_path)}")
    print(f"  Dimensions: {width_in}\" × {height_in}\" × {depth_in}\"")
    
    if scanner.add_training_example(image_path, width_cm, height_cm, depth_cm):
        print(f"  ✅ Added successfully!")
        return True
    else:
        print(f"  ❌ Failed to add")
        return False

def main():
    scanner = PackageVolumeScanner()
    
    # Add your training examples here
    # Format: (image_path, width_inches, height_inches, depth_inches)
    examples = [
        # Example format:
        # ("uploads/package1.jpg", 10.0, 16.0, 12.0),
        # Add your images here with dimensions:
        # ("path/to/image1.jpg", 10, 16, 12),  # 16"L × 10"W × 12"D
    ]
    
    if not examples:
        print("No training examples defined.")
        print("\nTo add examples, edit this script and add them to the 'examples' list.")
        print("Format: (image_path, width_inches, height_inches, depth_inches)")
        return
    
    print(f"Adding {len(examples)} training examples...")
    print("=" * 50)
    
    success_count = 0
    for image_path, width, height, depth in examples:
        if add_training_example(scanner, image_path, width, height, depth):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Successfully added {success_count}/{len(examples)} examples")
    print(f"📊 Total training examples: {len(scanner.training_data)}")

if __name__ == '__main__':
    main()

