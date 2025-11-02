#!/usr/bin/env python3
"""
Batch test script for multiple package images

Usage: python3 test_batch.py <image1> <image2> <image3> ...
"""

import sys
import os
from package_scanner import PackageVolumeScanner

def test_batch_images(image_paths):
    """Test multiple images in batch."""
    print("🧪 Batch Testing Package Volume Scanner")
    print("=" * 60)
    
    scanner = PackageVolumeScanner()
    results = []
    
    for i, image_path in enumerate(image_paths, 1):
        print(f"\n📷 Processing image {i}/{len(image_paths)}: {os.path.basename(image_path)}")
        
        if not os.path.exists(image_path):
            print(f"❌ File not found: {image_path}")
            results.append({'success': False, 'error': 'File not found', 'path': image_path})
            continue
        
        try:
            result = scanner.process_package(image_path)
            results.append(result)
            
            if result['success']:
                dims = result['dimensions']
                print(f"✅ Success: {dims['width_cm']:.1f} x {dims['height_cm']:.1f} x {dims['depth_cm']:.1f} cm = {dims['volume_liters']:.3f} L")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({'success': False, 'error': str(e), 'path': image_path})
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 BATCH RESULTS SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    if successful > 0:
        print("\n📏 SUCCESSFUL SCANS:")
        for i, result in enumerate(results):
            if result.get('success'):
                dims = result['dimensions']
                filename = os.path.basename(result['local_path'])
                print(f"   {i+1}. {filename}: {dims['volume_liters']:.3f} L")
    
    if successful < total:
        print("\n❌ FAILED SCANS:")
        for i, result in enumerate(results):
            if not result.get('success'):
                filename = os.path.basename(result.get('path', 'unknown'))
                print(f"   {i+1}. {filename}: {result.get('error', 'Unknown error')}")
    
    return results

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 test_batch.py <image1> <image2> <image3> ...")
        print()
        print("Examples:")
        print("  python3 test_batch.py package1.jpg package2.png")
        print("  python3 test_batch.py *.jpg")
        print("  python3 test_batch.py /path/to/image1.jpg /path/to/image2.png")
        sys.exit(1)
    
    image_paths = sys.argv[1:]
    results = test_batch_images(image_paths)
    
    print("\n🎉 Batch test completed!")

if __name__ == '__main__':
    main()
