"""
Package Volume Scanner Module

This module provides functionality to:
1. Detect package dimensions from images using computer vision
2. Calculate package volume
3. Upload images to cloud storage
"""

import cv2
import numpy as np
from PIL import Image
import os
import json
from typing import Tuple, Dict, Optional
import logging
from google.cloud import storage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PackageVolumeScanner:
    """Main class for scanning packages and calculating volume."""
    
    def __init__(self):
        """Initialize the scanner with configuration."""
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        self.bucket_name = os.getenv('GOOGLE_CLOUD_BUCKET_NAME')
        self.upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
        
        # Reference object dimensions for scale calibration (in cm)
        self.ref_width = float(os.getenv('REFERENCE_OBJECT_WIDTH', '10.0'))
        self.ref_height = float(os.getenv('REFERENCE_OBJECT_HEIGHT', '10.0'))
        
        # Calibration settings - adjust these for better accuracy
        # FIELD_OF_VIEW_CM: Estimated field of view in centimeters
        # Adjust based on your camera distance and setup
        # Example: If camera is 1 meter away and sees ~80cm wide, set to 80
        self.field_of_view_cm = float(os.getenv('FIELD_OF_VIEW_CM', '100.0'))
        
        # DEPTH_ESTIMATION_FACTOR: Multiplier for depth estimation
        # 0.8 = assumes depth is 80% of smallest visible dimension
        # Adjust based on typical package shapes (0.6-1.0 range)
        self.depth_factor = float(os.getenv('DEPTH_ESTIMATION_FACTOR', '0.8'))
        
        # Initialize Google Cloud Storage client
        self.storage_client = None
        if self.project_id and self.bucket_name:
            try:
                self.storage_client = storage.Client(project=self.project_id)
                logger.info("Google Cloud Storage client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize GCS client: {e}")
        
        # Create upload folder if it doesn't exist
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def detect_package_dimensions(self, image_path: str) -> Dict[str, float]:
        """
        Detect package dimensions from an image.
        
        Args:
            image_path: Path to the package image
            
        Returns:
            Dictionary containing width, height, depth, and volume
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find the largest contour (assuming it's the package)
            if not contours:
                raise ValueError("No contours found in image")
            
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Approximate the contour to a polygon
            epsilon = 0.02 * cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Calculate dimensions in pixels
            width_pixels = w
            height_pixels = h
            
            # Estimate depth (assuming roughly cubic package)
            # This is a simplified approach - in practice, you'd need stereo vision or multiple angles
            depth_pixels = min(width_pixels, height_pixels) * self.depth_factor
            
            # Convert pixels to real-world dimensions
            # This requires calibration with a known reference object
            scale_factor = self._calculate_scale_factor(image)
            
            width_cm = width_pixels * scale_factor
            height_cm = height_pixels * scale_factor
            depth_cm = depth_pixels * scale_factor
            
            # Calculate volume
            volume_cm3 = width_cm * height_cm * depth_cm
            
            # Convert cm to inches (1 cm = 0.393701 inches)
            width_in = width_cm * 0.393701
            height_in = height_cm * 0.393701
            depth_in = depth_cm * 0.393701
            
            # Convert cm³ to cubic feet (1 cm³ = 0.0000353147 cubic feet)
            volume_cubic_feet = volume_cm3 * 0.0000353147
            
            return {
                'width_cm': round(width_cm, 2),
                'height_cm': round(height_cm, 2),
                'depth_cm': round(depth_cm, 2),
                'width_in': round(width_in, 2),
                'height_in': round(height_in, 2),
                'depth_in': round(depth_in, 2),
                'volume_cm3': round(volume_cm3, 2),
                'volume_liters': round(volume_cm3 / 1000, 3),
                'volume_cubic_feet': round(volume_cubic_feet, 4)
            }
            
        except Exception as e:
            logger.error(f"Error detecting package dimensions: {e}")
            raise
    
    def _calculate_scale_factor(self, image: np.ndarray) -> float:
        """
        Calculate scale factor to convert pixels to real-world measurements.
        
        This is a simplified implementation. In practice, you would:
        1. Detect a reference object of known size
        2. Use stereo vision or multiple camera angles
        3. Use depth sensors or structured light
        
        Args:
            image: Input image
            
        Returns:
            Scale factor (cm per pixel)
        """
        # For demonstration, we'll use a heuristic based on image size
        # In a real implementation, you'd detect a reference object
        
        height, width = image.shape[:2]
        
        # Use configurable field of view for scale calculation
        # This can be calibrated by the user based on their camera setup
        # Formula: scale_factor = (real_world_size_cm) / (pixel_size)
        # We estimate: if image width/height represents FIELD_OF_VIEW_CM, then:
        scale_factor = self.field_of_view_cm / max(width, height)
        
        logger.info(f"Scale factor: {scale_factor:.6f} cm/pixel (FOV: {self.field_of_view_cm}cm, Image size: {max(width, height)}px)")
        
        return scale_factor
    
    def upload_to_cloud(self, local_path: str, cloud_filename: str) -> Optional[str]:
        """
        Upload image to Google Cloud Storage.
        
        Args:
            local_path: Local file path
            cloud_filename: Name for the file in cloud storage
            
        Returns:
            Public URL of uploaded file, or None if upload failed
        """
        if not self.storage_client:
            logger.warning("Google Cloud Storage not configured")
            return None
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(cloud_filename)
            
            # Upload file
            blob.upload_from_filename(local_path)
            
            # Make blob publicly readable
            blob.make_public()
            
            # Return public URL
            public_url = blob.public_url
            logger.info(f"File uploaded to: {public_url}")
            
            return public_url
            
        except Exception as e:
            logger.error(f"Error uploading to cloud storage: {e}")
            return None
    
    def process_package(self, image_path: str) -> Dict:
        """
        Complete package processing pipeline.
        
        Args:
            image_path: Path to the package image
            
        Returns:
            Dictionary containing processing results
        """
        try:
            # Generate unique filename for cloud storage
            filename = os.path.basename(image_path)
            name, ext = os.path.splitext(filename)
            timestamp = int(time.time())
            cloud_filename = f"packages/{timestamp}_{name}{ext}"
            
            # Detect dimensions
            dimensions = self.detect_package_dimensions(image_path)
            
            # Upload to cloud storage
            cloud_url = self.upload_to_cloud(image_path, cloud_filename)
            
            # Prepare results
            results = {
                'success': True,
                'dimensions': dimensions,
                'image_url': cloud_url,
                'local_path': image_path,
                'cloud_filename': cloud_filename,
                'timestamp': timestamp
            }
            
            logger.info(f"Package processed successfully: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error processing package: {e}")
            return {
                'success': False,
                'error': str(e),
                'image_path': image_path
            }


# Import time module for timestamp generation
import time
