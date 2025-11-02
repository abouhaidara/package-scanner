#!/usr/bin/env python3
"""
Interactive script to set up Google Cloud Storage configuration
"""

import os
import json
from pathlib import Path

def main():
    print("☁️ Google Cloud Storage Setup")
    print("=" * 50)
    print()
    
    print("You need to provide:")
    print("1. Google Cloud Project ID")
    print("2. Cloud Storage Bucket Name")
    print("3. Path to your service account JSON key file")
    print()
    print("📝 Don't have these yet? See CLOUD_STORAGE_SETUP.md for detailed instructions")
    print()
    
    # Get project ID
    project_id = input("Enter your Google Cloud Project ID: ").strip()
    if not project_id:
        print("❌ Project ID is required")
        return
    
    # Get bucket name
    bucket_name = input("Enter your Cloud Storage Bucket Name: ").strip()
    if not bucket_name:
        print("❌ Bucket name is required")
        return
    
    # Get credentials file path
    creds_path = input("Enter path to service account JSON key file (or press Enter to skip): ").strip()
    
    if creds_path:
        # Expand user path
        creds_path = os.path.expanduser(creds_path)
        
        # Check if file exists
        if not os.path.exists(creds_path):
            print(f"⚠️ Warning: File not found: {creds_path}")
            use_absolute = input("Continue anyway? (y/n): ").strip().lower()
            if use_absolute != 'y':
                return
        
        # Use absolute path
        creds_path = os.path.abspath(creds_path)
    else:
        # Use default application credentials (if set in environment)
        print("⚠️ No credentials file provided. Will use default application credentials.")
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
        if not creds_path:
            print("❌ GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
            print("   You can set it manually in your .env file later.")
    
    # Read current .env file
    env_file = Path('.env')
    env_content = env_file.read_text() if env_file.exists() else ""
    
    # Update the .env file
    lines = env_content.split('\n')
    updated_lines = []
    project_set = False
    bucket_set = False
    creds_set = False
    
    for line in lines:
        if line.startswith('# GOOGLE_CLOUD_PROJECT_ID') or line.startswith('GOOGLE_CLOUD_PROJECT_ID'):
            updated_lines.append(f'GOOGLE_CLOUD_PROJECT_ID={project_id}')
            project_set = True
        elif line.startswith('# GOOGLE_CLOUD_BUCKET_NAME') or line.startswith('GOOGLE_CLOUD_BUCKET_NAME'):
            updated_lines.append(f'GOOGLE_CLOUD_BUCKET_NAME={bucket_name}')
            bucket_set = True
        elif line.startswith('# GOOGLE_APPLICATION_CREDENTIALS') or line.startswith('GOOGLE_APPLICATION_CREDENTIALS'):
            if creds_path:
                updated_lines.append(f'GOOGLE_APPLICATION_CREDENTIALS={creds_path}')
                creds_set = True
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    # Add missing entries
    if not project_set:
        updated_lines.append(f'GOOGLE_CLOUD_PROJECT_ID={project_id}')
    if not bucket_set:
        updated_lines.append(f'GOOGLE_CLOUD_BUCKET_NAME={bucket_name}')
    if creds_path and not creds_set:
        updated_lines.append(f'GOOGLE_APPLICATION_CREDENTIALS={creds_path}')
    
    # Write updated .env file
    env_file.write_text('\n'.join(updated_lines))
    
    print()
    print("✅ Configuration updated in .env file!")
    print()
    print("📝 Next steps:")
    print("1. Test your configuration:")
    print("   python3 test_my_image.py uploads/your_image.jpg")
    print()
    print("2. Or start the web server:")
    print("   python3 app.py")
    print()
    print("3. Check if cloud storage is configured:")
    print("   curl http://127.0.0.1:5002/health")
    print()

if __name__ == '__main__':
    main()

