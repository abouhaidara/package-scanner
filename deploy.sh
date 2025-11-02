#!/bin/bash
# Production deployment script for Package Volume Scanner

set -e

echo "🚀 Package Volume Scanner - Production Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="package-scanner"
APP_DIR="/opt/package-scanner"
SERVICE_USER="www-data"
SERVICE_GROUP="www-data"
PORT=8000

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    log_error "This script should not be run as root"
    exit 1
fi

# Check if required tools are installed
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed"
        exit 1
    fi
    
    if ! command -v gunicorn &> /dev/null; then
        log_warn "Gunicorn not found, installing..."
        pip3 install gunicorn
    fi
    
    log_info "Dependencies check passed"
}

# Create application directory
setup_directories() {
    log_info "Setting up directories..."
    
    sudo mkdir -p $APP_DIR
    sudo mkdir -p $APP_DIR/uploads
    sudo mkdir -p $APP_DIR/logs
    sudo mkdir -p /etc/systemd/system
    
    log_info "Directories created"
}

# Install application
install_app() {
    log_info "Installing application..."
    
    # Copy application files
    sudo cp -r . $APP_DIR/
    
    # Install Python dependencies
    cd $APP_DIR
    sudo pip3 install -r requirements.txt
    
    # Set permissions
    sudo chown -R $SERVICE_USER:$SERVICE_GROUP $APP_DIR
    sudo chmod +x $APP_DIR/*.py
    
    log_info "Application installed"
}

# Create systemd service
create_service() {
    log_info "Creating systemd service..."
    
    sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null <<EOF
[Unit]
Description=Package Volume Scanner
After=network.target

[Service]
Type=exec
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=FLASK_ENV=production
Environment=PORT=$PORT
ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:$PORT --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    log_info "Systemd service created"
}

# Create environment file
create_env() {
    log_info "Creating environment configuration..."
    
    sudo tee $APP_DIR/.env > /dev/null <<EOF
# Production Environment Configuration
DEBUG=False
FLASK_ENV=production
PORT=$PORT
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Google Cloud Storage (configure as needed)
# GOOGLE_CLOUD_PROJECT_ID=your-project-id
# GOOGLE_CLOUD_BUCKET_NAME=your-bucket-name
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Reference object dimensions (in cm)
REFERENCE_OBJECT_WIDTH=10.0
REFERENCE_OBJECT_HEIGHT=10.0
EOF

    sudo chown $SERVICE_USER:$SERVICE_GROUP $APP_DIR/.env
    sudo chmod 600 $APP_DIR/.env
    
    log_info "Environment configuration created"
}

# Setup nginx (optional)
setup_nginx() {
    if command -v nginx &> /dev/null; then
        log_info "Setting up Nginx reverse proxy..."
        
        sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /uploads/ {
        alias $APP_DIR/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

        sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
        sudo nginx -t && sudo systemctl reload nginx
        
        log_info "Nginx configuration created"
    else
        log_warn "Nginx not found, skipping reverse proxy setup"
    fi
}

# Start services
start_services() {
    log_info "Starting services..."
    
    sudo systemctl daemon-reload
    sudo systemctl enable $APP_NAME
    sudo systemctl start $APP_NAME
    
    sleep 5
    
    if sudo systemctl is-active --quiet $APP_NAME; then
        log_info "Service started successfully"
    else
        log_error "Failed to start service"
        sudo systemctl status $APP_NAME
        exit 1
    fi
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    sleep 10
    
    if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
        log_info "Health check passed"
    else
        log_error "Health check failed"
        exit 1
    fi
}

# Main deployment process
main() {
    log_info "Starting deployment process..."
    
    check_dependencies
    setup_directories
    install_app
    create_service
    create_env
    setup_nginx
    start_services
    health_check
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "📝 Service Information:"
    echo "   Service: $APP_NAME"
    echo "   Status: $(sudo systemctl is-active $APP_NAME)"
    echo "   Port: $PORT"
    echo "   URL: http://localhost:$PORT"
    echo ""
    echo "🔧 Management Commands:"
    echo "   Start:   sudo systemctl start $APP_NAME"
    echo "   Stop:    sudo systemctl stop $APP_NAME"
    echo "   Restart: sudo systemctl restart $APP_NAME"
    echo "   Status:  sudo systemctl status $APP_NAME"
    echo "   Logs:    sudo journalctl -u $APP_NAME -f"
    echo ""
    echo "📊 Monitoring:"
    echo "   Health:  curl http://localhost:$PORT/health"
    echo "   Test:    curl -X POST -F 'file=@test.jpg' http://localhost:$PORT/api/scan"
}

# Run main function
main "$@"
