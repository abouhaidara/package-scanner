#!/usr/bin/env python3
"""
Deployment helper script for Package Volume Scanner

This script helps you deploy the Package Volume Scanner to various platforms.
"""

import os
import sys
import subprocess
import json
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

def check_dependencies():
    """Check if required tools are installed."""
    print("🔍 Checking deployment dependencies...")
    
    tools = {
        'python3': 'Python 3.8+',
        'pip3': 'pip3 package manager',
        'docker': 'Docker (optional)',
        'docker-compose': 'Docker Compose (optional)',
        'gunicorn': 'Gunicorn WSGI server (optional)',
        'nginx': 'Nginx web server (optional)'
    }
    
    available = {}
    for tool, description in tools.items():
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
            available[tool] = True
            print(f"✅ {tool}: {description}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            available[tool] = False
            print(f"❌ {tool}: {description} (not found)")
    
    return available

def deploy_local():
    """Deploy locally with Gunicorn."""
    print("🏠 Deploying locally with Gunicorn...")
    
    # Install Gunicorn if not available
    if not run_command("pip3 install gunicorn", "Installing Gunicorn"):
        return False
    
    # Create production environment
    env_content = """# Production Environment
DEBUG=False
FLASK_ENV=production
PORT=8000
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
SECRET_KEY=your-secret-key-change-this
"""
    
    with open('.env.production', 'w') as f:
        f.write(env_content)
    
    print("✅ Production environment created")
    
    # Start with Gunicorn
    print("🚀 Starting production server...")
    print("   URL: http://localhost:8000")
    print("   Press Ctrl+C to stop")
    
    try:
        subprocess.run([
            "gunicorn", "-w", "4", "-b", "0.0.0.0:8000", 
            "--timeout", "120", "--keep-alive", "2",
            "app:app"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    
    return True

def deploy_docker():
    """Deploy with Docker."""
    print("🐳 Deploying with Docker...")
    
    if not run_command("docker --version", "Checking Docker"):
        print("❌ Docker not found. Please install Docker first.")
        return False
    
    # Build Docker image
    if not run_command("docker build -t package-scanner .", "Building Docker image"):
        return False
    
    # Run Docker container
    print("🚀 Starting Docker container...")
    print("   URL: http://localhost:8000")
    print("   Press Ctrl+C to stop")
    
    try:
        subprocess.run([
            "docker", "run", "-p", "8000:8000",
            "-e", "FLASK_ENV=production",
            "-e", "DEBUG=False",
            "package-scanner"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Container stopped")
    
    return True

def deploy_docker_compose():
    """Deploy with Docker Compose."""
    print("🐳 Deploying with Docker Compose...")
    
    if not run_command("docker-compose --version", "Checking Docker Compose"):
        print("❌ Docker Compose not found. Please install Docker Compose first.")
        return False
    
    # Start services
    print("🚀 Starting services with Docker Compose...")
    print("   URL: http://localhost:8000")
    print("   Press Ctrl+C to stop")
    
    try:
        subprocess.run(["docker-compose", "up", "--build"])
    except KeyboardInterrupt:
        print("\n🛑 Services stopped")
        subprocess.run(["docker-compose", "down"])
    
    return True

def deploy_heroku():
    """Deploy to Heroku."""
    print("☁️ Deploying to Heroku...")
    
    if not run_command("heroku --version", "Checking Heroku CLI"):
        print("❌ Heroku CLI not found. Please install it first.")
        print("   https://devcenter.heroku.com/articles/heroku-cli")
        return False
    
    # Create Heroku app
    app_name = input("Enter Heroku app name (or press Enter for auto-generated): ").strip()
    if not app_name:
        app_name = f"package-scanner-{os.getenv('USER', 'user')}"
    
    if not run_command(f"heroku create {app_name}", f"Creating Heroku app: {app_name}"):
        return False
    
    # Set environment variables
    env_vars = {
        'FLASK_ENV': 'production',
        'DEBUG': 'False',
        'PORT': '8000'
    }
    
    for key, value in env_vars.items():
        if not run_command(f"heroku config:set {key}={value}", f"Setting {key}"):
            return False
    
    # Deploy
    if not run_command("git add .", "Staging files"):
        return False
    
    if not run_command("git commit -m 'Deploy to Heroku'", "Committing changes"):
        return False
    
    if not run_command("git push heroku main", "Deploying to Heroku"):
        return False
    
    print(f"✅ Deployed to Heroku!")
    print(f"   URL: https://{app_name}.herokuapp.com")
    
    return True

def deploy_google_cloud():
    """Deploy to Google Cloud Run."""
    print("☁️ Deploying to Google Cloud Run...")
    
    if not run_command("gcloud --version", "Checking Google Cloud CLI"):
        print("❌ Google Cloud CLI not found. Please install it first.")
        print("   https://cloud.google.com/sdk/docs/install")
        return False
    
    project_id = input("Enter Google Cloud Project ID: ").strip()
    if not project_id:
        print("❌ Project ID is required")
        return False
    
    if not run_command(f"gcloud config set project {project_id}", "Setting project"):
        return False
    
    # Build and deploy
    service_name = "package-scanner"
    region = "us-central1"
    
    if not run_command(f"gcloud builds submit --tag gcr.io/{project_id}/{service_name}", "Building container"):
        return False
    
    if not run_command(f"gcloud run deploy {service_name} --image gcr.io/{project_id}/{service_name} --platform managed --region {region} --allow-unauthenticated --port 8000", "Deploying to Cloud Run"):
        return False
    
    print(f"✅ Deployed to Google Cloud Run!")
    print(f"   Service: {service_name}")
    print(f"   Region: {region}")
    
    return True

def main():
    """Main deployment menu."""
    print("🚀 Package Volume Scanner - Deployment Helper")
    print("=" * 50)
    
    # Check dependencies
    available = check_dependencies()
    print()
    
    # Show deployment options
    options = [
        ("1", "Local deployment with Gunicorn", deploy_local, True),
        ("2", "Docker deployment", deploy_docker, available.get('docker', False)),
        ("3", "Docker Compose deployment", deploy_docker_compose, available.get('docker-compose', False)),
        ("4", "Heroku deployment", deploy_heroku, available.get('heroku', False)),
        ("5", "Google Cloud Run deployment", deploy_google_cloud, available.get('gcloud', False)),
    ]
    
    print("📋 Available deployment options:")
    for option, description, func, available_flag in options:
        status = "✅" if available_flag else "❌ (not available)"
        print(f"   {option}. {description} {status}")
    
    print()
    
    # Get user choice
    while True:
        choice = input("Select deployment option (1-5) or 'q' to quit: ").strip()
        
        if choice.lower() == 'q':
            print("👋 Goodbye!")
            return
        
        if choice in ['1', '2', '3', '4', '5']:
            option, description, func, available_flag = options[int(choice) - 1]
            
            if not available_flag:
                print(f"❌ {description} is not available. Please install required dependencies.")
                continue
            
            print(f"\n🚀 Starting {description}...")
            print("=" * 50)
            
            try:
                success = func()
                if success:
                    print(f"\n🎉 {description} completed successfully!")
                else:
                    print(f"\n❌ {description} failed!")
            except KeyboardInterrupt:
                print(f"\n🛑 {description} cancelled by user")
            except Exception as e:
                print(f"\n❌ {description} failed with error: {e}")
            
            break
        else:
            print("❌ Invalid choice. Please select 1-5 or 'q' to quit.")

if __name__ == '__main__':
    main()
