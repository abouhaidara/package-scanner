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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'avif', 'webp'}

# Calibration settings (for accuracy improvement)
FIELD_OF_VIEW_CM = os.getenv('FIELD_OF_VIEW_CM', '100.0')  # Adjust for better accuracy
DEPTH_ESTIMATION_FACTOR = os.getenv('DEPTH_ESTIMATION_FACTOR', '0.8')  # Depth estimation multiplier

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


@app.route('/train', methods=['GET', 'POST'])
def train():
    """Add training data with known dimensions."""
    if request.method == 'GET':
        # Show current training data count
        training_count = len(scanner.training_data)
        return render_template('train.html', training_count=training_count)
    
    # Handle POST request
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('train'))
    
    file = request.files['file']
    width_in = request.form.get('width')
    height_in = request.form.get('height')
    depth_in = request.form.get('depth')
    
    if not file or file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('train'))
    
    if not width_in or not height_in or not depth_in:
        flash('Please provide all dimensions', 'error')
        return redirect(url_for('train'))
    
    try:
        width_in = float(width_in)
        height_in = float(height_in)
        depth_in = float(depth_in)
    except ValueError:
        flash('Invalid dimension values', 'error')
        return redirect(url_for('train'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"train_{timestamp}_{name}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            
            # Convert inches to cm
            width_cm = width_in * 2.54
            height_cm = height_in * 2.54
            depth_cm = depth_in * 2.54
            
            # Add training example
            logger.info(f"Adding training example: {filepath}, dimensions: {width_cm}cm × {height_cm}cm × {depth_cm}cm")
            if scanner.add_training_example(filepath, width_cm, height_cm, depth_cm):
                total_examples = len(scanner.training_data)
                logger.info(f"Training example added successfully! Total: {total_examples}")
                flash(f'✅ Training example added successfully! Total examples: {total_examples}', 'success')
            else:
                logger.error("Failed to add training example")
                flash('❌ Failed to add training example. Please check the image and try again.', 'error')
            
            return redirect(url_for('train'))
            
        except Exception as e:
            logger.error(f"Error processing training data: {e}", exc_info=True)
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('train'))
    
    flash('Invalid file type', 'error')
    return redirect(url_for('train'))


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    """Handle file upload and processing."""
    logger.info(f"Upload route called with method: {request.method}")
    
    # Handle GET requests (shouldn't happen, but handle gracefully)
    if request.method == 'GET':
        logger.info("GET request to /upload, redirecting to index")
        return redirect(url_for('index'))
    
    # Handle POST requests
    logger.info("POST request received")
    
    if 'file' not in request.files:
        logger.warning("No file in request.files")
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    logger.info(f"File received: {file.filename if file else 'None'}")
    
    if file.filename == '':
        logger.warning("Empty filename")
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        logger.info(f"Processing file: {filename}")
        
        # Add timestamp to filename to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{timestamp}_{name}{ext}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"Saving file to: {filepath}")
        
        try:
            file.save(filepath)
            logger.info(f"File saved successfully to {filepath}")
        except Exception as e:
            logger.error(f"Error saving file: {e}", exc_info=True)
            flash(f'Error saving file: {str(e)}', 'error')
            return redirect(url_for('index'))
        
        # Process the package
        # The app automatically uses:
        # 1. Credit card detection (if card is in photo) - BEST ACCURACY
        # 2. Training data (if similar examples exist)
        # 3. Smart estimation (automatic fallback)
        try:
            logger.info("Starting package processing...")
            result = scanner.process_package(filepath)
            logger.info(f"Processing result: success={result.get('success')}")
            
            if result.get('success'):
                # Convert timestamp to readable format if it's a Unix timestamp
                if isinstance(result.get('timestamp'), int):
                    result['timestamp'] = datetime.fromtimestamp(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                elif not isinstance(result.get('timestamp'), str):
                    result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                logger.info(f"Package processed successfully, rendering results page")
                logger.info(f"Result keys: {result.keys()}")
                logger.info(f"Dimensions: {result.get('dimensions')}")
                
                try:
                    return render_template('results.html', result=result)
                except Exception as template_error:
                    logger.error(f"Error rendering template: {template_error}", exc_info=True)
                    flash(f'Error displaying results: {str(template_error)}', 'error')
                    return redirect(url_for('index'))
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Package processing failed: {error_msg}")
                logger.error(f"Full result: {result}")
                flash(f'Error processing package: {error_msg}', 'error')
                return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Exception processing package: {e}", exc_info=True)
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Full traceback: {error_details}")
            flash(f'Error processing package: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    logger.warning(f"Invalid file type: {file.filename if file else 'None'}")
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
