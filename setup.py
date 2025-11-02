#!/usr/bin/env python3
"""
Setup script for Package Volume Scanner

This script helps set up the environment and install dependencies.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def install_dependencies():
    """Install required Python packages."""
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    return True


def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    directories = ['uploads', 'logs', 'static']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True


def setup_environment():
    """Set up environment configuration."""
    print("⚙️ Setting up environment...")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your configuration")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️ No .env.example found, creating basic .env file")
        with open(env_file, 'w') as f:
            f.write("""# Environment Configuration
DEBUG=True
PORT=5000
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Google Cloud Storage Configuration (optional)
# GOOGLE_CLOUD_PROJECT_ID=your-project-id
# GOOGLE_CLOUD_BUCKET_NAME=your-bucket-name
# GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json

# Reference object dimensions (in cm)
REFERENCE_OBJECT_WIDTH=10.0
REFERENCE_OBJECT_HEIGHT=10.0
""")
        print("✅ Created basic .env file")
    
    return True


def check_opencv():
    """Check if OpenCV is properly installed."""
    print("🔍 Checking OpenCV installation...")
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__} installed")
        return True
    except ImportError:
        print("❌ OpenCV not found. Please install it manually:")
        print("   pip install opencv-python")
        return False


def main():
    """Main setup function."""
    print("🚀 Package Volume Scanner Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Check OpenCV
    if not check_opencv():
        print("\n❌ Setup failed - OpenCV not available")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Setup failed during directory creation")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Setup failed during environment setup")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration")
    print("2. Set up Google Cloud Storage (optional)")
    print("3. Run the web app: python app.py")
    print("4. Or use CLI: python cli.py <image_path>")
    print("\nFor more information, see README.md")


if __name__ == '__main__':
    main()
