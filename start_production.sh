#!/bin/bash
# Production start script for Package Volume Scanner

set -e

# Configuration
APP_NAME="package-scanner"
PORT=${PORT:-8000}
WORKERS=${WORKERS:-4}
TIMEOUT=${TIMEOUT:-120}
KEEPALIVE=${KEEPALIVE:-2}
MAX_REQUESTS=${MAX_REQUESTS:-1000}
MAX_REQUESTS_JITTER=${MAX_REQUESTS_JITTER:-100}

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    log_error "app.py not found. Please run this script from the package_scanner directory."
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    log_info "Activating virtual environment..."
    source venv/bin/activate
fi

# Install/upgrade dependencies
log_info "Installing dependencies..."
pip install -r requirements.txt
pip install gunicorn

# Create necessary directories
log_info "Creating directories..."
mkdir -p uploads logs

# Set production environment variables
export FLASK_ENV=production
export DEBUG=False
export PORT=$PORT

# Load environment file if it exists
if [ -f ".env.production" ]; then
    log_info "Loading production environment..."
    export $(cat .env.production | grep -v '^#' | xargs)
elif [ -f ".env" ]; then
    log_info "Loading environment..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Generate secret key if not set
if [ -z "$SECRET_KEY" ]; then
    log_warn "SECRET_KEY not set, generating one..."
    export SECRET_KEY=$(openssl rand -hex 32)
fi

# Health check function
health_check() {
    log_info "Performing health check..."
    sleep 5
    
    if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
        log_info "Health check passed"
        return 0
    else
        log_error "Health check failed"
        return 1
    fi
}

# Start the application
log_info "Starting Package Volume Scanner..."
log_info "Configuration:"
log_info "  Port: $PORT"
log_info "  Workers: $WORKERS"
log_info "  Timeout: $TIMEOUT"
log_info "  Environment: $FLASK_ENV"
log_info "  Debug: $DEBUG"

# Start Gunicorn
exec gunicorn \
    -w $WORKERS \
    -b 0.0.0.0:$PORT \
    --timeout $TIMEOUT \
    --keep-alive $KEEPALIVE \
    --max-requests $MAX_REQUESTS \
    --max-requests-jitter $MAX_REQUESTS_JITTER \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --preload \
    app:app
