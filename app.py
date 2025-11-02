"""
Flask Web Application for Package Volume Scanner

This module provides a web interface for uploading package images
and displaying volume calculation results.
"""

from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import json
import logging
from datetime import datetime
from package_scanner import PackageVolumeScanner
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize package scanner
scanner = PackageVolumeScanner()

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def index():
    """Main page with upload form."""
    return render_template('index.html')


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    """Handle file upload and processing."""
    # Handle GET requests (shouldn't happen, but handle gracefully)
    if request.method == 'GET':
        return redirect(url_for('index'))
    
    # Handle POST requests
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Add timestamp to filename to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{timestamp}_{name}{ext}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the package
        try:
            result = scanner.process_package(filepath)
            
            if result.get('success'):
                # Convert timestamp to readable format if it's a Unix timestamp
                if isinstance(result.get('timestamp'), int):
                    result['timestamp'] = datetime.fromtimestamp(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                elif not isinstance(result.get('timestamp'), str):
                    result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                logger.info(f"Package processed successfully: {result}")
                return render_template('results.html', result=result)
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Package processing failed: {error_msg}")
                flash(f'Error processing package: {error_msg}')
                return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Exception processing package: {e}", exc_info=True)
            flash(f'Error processing package: {str(e)}')
            return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload an image file.')
    return redirect(url_for('index'))


@app.route('/api/scan', methods=['POST'])
def api_scan():
    """API endpoint for package scanning."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{timestamp}_{name}{ext}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the package
        result = scanner.process_package(filepath)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/results')
def api_results():
    """API endpoint to get recent processing results."""
    # This would typically query a database
    # For now, return a simple response
    return jsonify({
        'message': 'Results endpoint - implement database integration for persistent storage'
    })


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'scanner_configured': scanner.storage_client is not None
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Package Scanner on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Google Cloud Storage configured: {scanner.storage_client is not None}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
