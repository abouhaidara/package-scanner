#!/usr/bin/env python3
"""
Command Line Interface for Package Volume Scanner

This script provides a command-line interface for scanning packages
without using the web application.
"""

import argparse
import sys
import os
from package_scanner import PackageVolumeScanner
import json


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Package Volume Scanner - Calculate package dimensions and volume from images'
    )
    
    parser.add_argument(
        'image_path',
        help='Path to the package image file'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file for results (JSON format)',
        default=None
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--no-cloud',
        action='store_true',
        help='Skip cloud storage upload'
    )
    
    args = parser.parse_args()
    
    # Check if image file exists
    if not os.path.exists(args.image_path):
        print(f"Error: Image file '{args.image_path}' not found")
        sys.exit(1)
    
    # Initialize scanner
    scanner = PackageVolumeScanner()
    
    if args.verbose:
        print(f"Processing image: {args.image_path}")
        print(f"Cloud storage configured: {scanner.storage_client is not None}")
    
    try:
        # Process the package
        result = scanner.process_package(args.image_path)
        
        if result['success']:
            print("\n" + "="*50)
            print("📦 PACKAGE SCAN RESULTS")
            print("="*50)
            
            dimensions = result['dimensions']
            print(f"\n📏 Dimensions:")
            print(f"   Width:  {dimensions['width_cm']} cm")
            print(f"   Height: {dimensions['height_cm']} cm")
            print(f"   Depth:  {dimensions['depth_cm']} cm")
            
            print(f"\n🧮 Volume:")
            print(f"   {dimensions['volume_cm3']} cm³")
            print(f"   {dimensions['volume_liters']} liters")
            
            if result.get('image_url'):
                print(f"\n☁️ Cloud Storage:")
                print(f"   URL: {result['image_url']}")
            elif args.no_cloud:
                print(f"\n☁️ Cloud Storage: Skipped (--no-cloud flag)")
            else:
                print(f"\n☁️ Cloud Storage: Not configured")
            
            print(f"\n📁 Local file: {result['local_path']}")
            print(f"🕒 Processed: {result['timestamp']}")
            
            # Save results to file if requested
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Results saved to: {args.output}")
            
            print("\n" + "="*50)
            
        else:
            print(f"❌ Error processing package: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
