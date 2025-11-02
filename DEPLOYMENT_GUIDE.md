# 🚀 Package Volume Scanner - Deployment Guide

This guide covers multiple deployment options for your Package Volume Scanner, from simple local deployment to production cloud deployment.

## 📋 Pre-Deployment Checklist

### ✅ Requirements
- Python 3.8+
- OpenCV dependencies
- Google Cloud Storage account (optional)
- Domain name (for production)

### ✅ Environment Setup
```bash
# Install production dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your production settings
```

## 🌐 Deployment Options

### **Option 1: Local Production Server**

#### Using Gunicorn (Recommended)
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# With environment variables
PORT=8000 gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

#### Using Waitress (Windows-friendly)
```bash
# Install Waitress
pip install waitress

# Run with Waitress
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

### **Option 2: Docker Deployment**

#### Create Dockerfile
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Set environment variables
ENV PORT=8000
ENV FLASK_ENV=production

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

#### Build and Run Docker Container
```bash
# Build the image
docker build -t package-scanner .

# Run the container
docker run -p 8000:8000 -e GOOGLE_CLOUD_PROJECT_ID=your-project package-scanner

# With volume mount for uploads
docker run -p 8000:8000 -v $(pwd)/uploads:/app/uploads package-scanner
```

### **Option 3: Cloud Deployment**

#### Google Cloud Run
```bash
# Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/package-scanner

# Deploy to Cloud Run
gcloud run deploy package-scanner \
  --image gcr.io/PROJECT-ID/package-scanner \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000
```

#### Heroku Deployment
```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Create Heroku app
heroku create your-package-scanner

# Set environment variables
heroku config:set GOOGLE_CLOUD_PROJECT_ID=your-project-id
heroku config:set GOOGLE_CLOUD_BUCKET_NAME=your-bucket-name

# Deploy
git push heroku main
```

#### AWS Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init

# Create environment
eb create production

# Deploy
eb deploy
```

### **Option 4: VPS Deployment**

#### Using Nginx + Gunicorn
```bash
# Install Nginx
sudo apt update
sudo apt install nginx

# Install Gunicorn
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/package-scanner.service
```

#### Systemd Service File
```ini
[Unit]
Description=Package Volume Scanner
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/package_scanner
Environment=PATH=/path/to/package_scanner/venv/bin
ExecStart=/path/to/package_scanner/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads {
        alias /path/to/package_scanner/uploads;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 🔧 Production Configuration

### **Environment Variables (.env)**
```bash
# Production Settings
DEBUG=False
PORT=8000
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Google Cloud Storage
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Security
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# Database (if needed)
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### **Security Considerations**
- Set `DEBUG=False` in production
- Use strong `SECRET_KEY`
- Enable HTTPS with SSL certificates
- Set up proper CORS policies
- Implement rate limiting
- Use environment variables for sensitive data

## 📊 Monitoring and Logging

### **Application Monitoring**
```python
# Add to app.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/package_scanner.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Package Scanner startup')
```

### **Health Checks**
```bash
# Add health check endpoint
curl http://your-domain.com/health

# Monitor with external services
# - UptimeRobot
# - Pingdom
# - StatusCake
```

## 🚀 Quick Deployment Scripts

### **Local Production Start**
```bash
#!/bin/bash
# start_production.sh

cd /path/to/package_scanner

# Activate virtual environment
source venv/bin/activate

# Set production environment
export FLASK_ENV=production
export DEBUG=False

# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### **Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'

services:
  package-scanner:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - GOOGLE_CLOUD_PROJECT_ID=${GOOGLE_CLOUD_PROJECT_ID}
      - GOOGLE_CLOUD_BUCKET_NAME=${GOOGLE_CLOUD_BUCKET_NAME}
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped
```

## 📈 Performance Optimization

### **Production Optimizations**
- Use Gunicorn with multiple workers
- Enable gzip compression
- Set up CDN for static files
- Implement caching
- Use database for result storage
- Optimize image processing

### **Scaling Considerations**
- Horizontal scaling with load balancer
- Database for persistent storage
- Redis for caching
- Message queue for background tasks
- Container orchestration (Kubernetes)

## 🔍 Troubleshooting

### **Common Issues**
1. **Port conflicts**: Use different ports
2. **Permission errors**: Check file permissions
3. **Memory issues**: Optimize image processing
4. **SSL certificates**: Use Let's Encrypt

### **Debug Commands**
```bash
# Check if service is running
systemctl status package-scanner

# View logs
journalctl -u package-scanner -f

# Test endpoints
curl http://localhost:8000/health
```

## 📝 Deployment Checklist

- [ ] Environment variables configured
- [ ] Security settings applied
- [ ] SSL certificate installed
- [ ] Monitoring set up
- [ ] Backup strategy implemented
- [ ] Performance testing completed
- [ ] Documentation updated

Choose the deployment option that best fits your needs and infrastructure!
