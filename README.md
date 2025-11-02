# 📦 Package Volume Scanner

A comprehensive tool that automatically scans packages to determine their volume using computer vision and stores photos on cloud storage.

## ✨ Features

1. **🔍 Automatic Volume Calculation**: Uses OpenCV computer vision to detect package dimensions and calculate volume
2. **☁️ Cloud Storage Integration**: Automatically uploads package photos to Google Cloud Storage
3. **🌐 Web Interface**: Beautiful, modern web interface for uploading and processing package images
4. **💻 Command Line Interface**: CLI tool for batch processing and automation
5. **📊 Detailed Results**: Comprehensive dimension analysis with volume calculations
6. **🔧 Configurable**: Flexible configuration for different use cases

## 🚀 Quick Start

### Option 1: Automated Setup
```bash
# Clone or download the project
cd package_scanner

# Run the setup script
python setup.py

# Start the web application
python app.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the application
python app.py
```

## 📋 Installation Requirements

- **Python 3.8+**
- **OpenCV** (for computer vision)
- **Google Cloud Storage** (optional, for cloud storage)
- **Camera or image files** (for input)

## ⚠️ Deployment Note

**Vercel/Netlify Functions are NOT supported** - OpenCV requires system libraries not available in serverless environments.

**Recommended platforms:** Railway, Render, Google Cloud Run, or Fly.io (all support Docker/OpenCV)

See `QUICK_DEPLOY.md` for deployment instructions.

## 🔧 Configuration

### Environment Variables (.env file)

```bash
# Application Settings
DEBUG=True
PORT=5000
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Google Cloud Storage (Optional)
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Calibration Settings
REFERENCE_OBJECT_WIDTH=10.0
REFERENCE_OBJECT_HEIGHT=10.0
```

### Google Cloud Storage Setup

1. Create a Google Cloud Project
2. Enable Cloud Storage API
3. Create a service account
4. Download the JSON key file
5. Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

## 💻 Usage

### Web Interface
1. Start the application: `python app.py`
2. Open browser to `http://localhost:5000`
3. Upload a package image
4. View results with dimensions and volume

### Command Line Interface
```bash
# Basic usage
python cli.py package_image.jpg

# With output file
python cli.py package_image.jpg --output results.json

# Verbose output
python cli.py package_image.jpg --verbose

# Skip cloud upload
python cli.py package_image.jpg --no-cloud
```

### Programmatic Usage
```python
from package_scanner import PackageVolumeScanner

# Initialize scanner
scanner = PackageVolumeScanner()

# Process package
result = scanner.process_package('package_image.jpg')

if result['success']:
    print(f"Volume: {result['dimensions']['volume_liters']} liters")
    print(f"Dimensions: {result['dimensions']['width_cm']} x {result['dimensions']['height_cm']} x {result['dimensions']['depth_cm']} cm")
```

## 🌐 API Endpoints

### REST API
- `POST /api/scan` - Upload and process a package image
- `GET /api/results` - Get processing results
- `GET /health` - Health check endpoint

### Example API Usage
```bash
# Upload and scan
curl -X POST -F "file=@package.jpg" http://localhost:5000/api/scan

# Health check
curl http://localhost:5000/health
```

## 📊 Output Format

The tool provides detailed results including:

```json
{
  "success": true,
  "dimensions": {
    "width_cm": 25.5,
    "height_cm": 15.2,
    "depth_cm": 12.8,
    "volume_cm3": 4956.48,
    "volume_liters": 4.956
  },
  "image_url": "https://storage.googleapis.com/bucket/packages/image.jpg",
  "local_path": "uploads/image.jpg",
  "cloud_filename": "packages/image.jpg",
  "timestamp": 1234567890
}
```

## 🔬 How It Works

1. **Image Processing**: Uses OpenCV to load and preprocess the image
2. **Edge Detection**: Applies Canny edge detection to find package boundaries
3. **Contour Analysis**: Finds the largest contour (assumed to be the package)
4. **Dimension Calculation**: Calculates width, height, and estimates depth
5. **Volume Calculation**: Computes volume using the detected dimensions
6. **Cloud Upload**: Uploads the image to Google Cloud Storage (if configured)

## 🛠️ Advanced Features

### Calibration
The tool uses reference objects for scale calibration. You can adjust the calibration by modifying the reference object dimensions in the `.env` file.

### Batch Processing
Use the CLI tool for batch processing multiple images:

```bash
for image in *.jpg; do
    python cli.py "$image" --output "results_${image%.jpg}.json"
done
```

### Custom Dimensions
For more accurate results, you can modify the `detect_package_dimensions` method to use:
- Stereo vision
- Multiple camera angles
- Depth sensors
- Structured light

## 📁 Project Structure

```
package_scanner/
├── app.py                 # Flask web application
├── cli.py                 # Command line interface
├── package_scanner.py     # Core scanning logic
├── example.py            # Usage examples
├── setup.py              # Setup script
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── README.md            # This file
├── templates/           # HTML templates
│   ├── index.html      # Main upload page
│   └── results.html    # Results display page
└── uploads/            # Upload directory (created automatically)
```

## 🐛 Troubleshooting

### Common Issues

1. **OpenCV not found**: Install with `pip install opencv-python`
2. **Cloud storage errors**: Check your Google Cloud credentials
3. **No contours detected**: Ensure good lighting and clear package edges
4. **Inaccurate dimensions**: Adjust calibration settings or improve image quality

### Debug Mode
Enable debug mode in `.env`:
```bash
DEBUG=True
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. See LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the example scripts
3. Open an issue on GitHub

## 🔮 Future Enhancements

- [ ] Support for multiple package types
- [ ] Integration with shipping APIs
- [ ] Mobile app version
- [ ] Real-time camera processing
- [ ] Machine learning for better accuracy
- [ ] Database integration for result storage
