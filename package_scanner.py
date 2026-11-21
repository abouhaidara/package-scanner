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
        self.upload_folder = os.getenv('UPLOAD_FOLDER', '/tmp/uploads' if os.getenv('VERCEL') else 'uploads')
        
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
    
    def detect_package_dimensions(self, image_path: str, known_dimension_cm: Optional[float] = None, dimension_type: str = 'width') -> Dict[str, float]:
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
            
            # Try adaptive threshold for better handling of varying lighting
            # This adapts to local lighting conditions, better than global threshold
            adaptive_thresh = cv2.adaptiveThreshold(
                blurred, 
                255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 
                11, 
                2
            )
            
            # Apply edge detection on adaptive threshold (better for varying lighting)
            edges_adaptive = cv2.Canny(adaptive_thresh, 50, 150)
            
            # Also try Canny on original blurred image as fallback
            edges_original = cv2.Canny(blurred, 50, 150)
            
            # Find contours from both methods
            contours_adaptive, _ = cv2.findContours(edges_adaptive, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours_original, _ = cv2.findContours(edges_original, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Combine contours and find the largest
            all_contours = list(contours_adaptive) + list(contours_original)
            
            if not all_contours:
                raise ValueError("No contours found in image")
            
            # Sort contours by area (largest first)
            sorted_contours = sorted(all_contours, key=cv2.contourArea, reverse=True)
            largest_contour = sorted_contours[0]
            
            # Try to detect credit card for automatic calibration (check all contours)
            # We'll calculate scale factor after we have pixel dimensions
            scale_factor = None
            
            # Approximate the contour to a polygon
            epsilon = 0.02 * cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)
            
            # Use minAreaRect for better handling of rotated packages
            # This gives us the minimum area rotated rectangle (handles rotation automatically)
            rect = cv2.minAreaRect(largest_contour)
            # rect format: ((center_x, center_y), (width, height), angle)
            width_rect = rect[1][0]
            height_rect = rect[1][1]
            
            # Use the larger dimension as length, smaller as width
            # This automatically handles rotation
            width_pixels = min(width_rect, height_rect)
            height_pixels = max(width_rect, height_rect)
            
            logger.info(f"Detected package: {width_pixels:.1f}px × {height_pixels:.1f}px (minAreaRect, handles rotation)")
            
            # Estimate depth (assuming roughly cubic package)
            # This is a simplified approach - in practice, you'd need stereo vision or multiple angles
            depth_pixels = min(width_pixels, height_pixels) * self.depth_factor
            
            # Convert pixels to real-world dimensions using calculated scale factor
            # If user provided a known dimension, use it to calibrate the scale factor
            if known_dimension_cm:
                if dimension_type == 'width':
                    # User knows the width - use it to calculate accurate scale
                    scale_factor = known_dimension_cm / width_pixels
                    logger.info(f"Calibrated using known width: {known_dimension_cm}cm = {width_pixels}px, scale: {scale_factor:.6f} cm/pixel")
                elif dimension_type == 'height':
                    # User knows the height - use it to calculate accurate scale
                    scale_factor = known_dimension_cm / height_pixels
                    logger.info(f"Calibrated using known height: {known_dimension_cm}cm = {height_pixels}px, scale: {scale_factor:.6f} cm/pixel")
            else:
                # Calculate scale factor using best available method
                scale_factor = self._calculate_scale_factor(image, all_contours)
            
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
                'width_pixels': width_pixels,
                'height_pixels': height_pixels,
                'depth_pixels': depth_pixels,
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
    
    def _detect_credit_card(self, image: np.ndarray, contours) -> Optional[float]:
        """
        Try to detect a credit card in the image for automatic calibration.
        Credit card standard size: 8.56cm × 5.398cm (ISO/IEC 7810 ID-1)
        
        Args:
            image: Input image
            contours: List of detected contours
            
        Returns:
            Scale factor if credit card detected, None otherwise
        """
        if not contours:
            return None
        
        # Credit card aspect ratio: 8.56 / 5.398 ≈ 1.586
        credit_card_aspect_ratio = 8.56 / 5.398  # ≈ 1.586
        tolerance = 0.15  # 15% tolerance for aspect ratio matching
        
        # Credit card typical size range in pixels (for filtering)
        min_card_size = 100  # pixels
        max_card_size = max(image.shape[:2]) * 0.5  # Max 50% of image
        
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            
            # Filter by size
            if area < min_card_size * min_card_size or area > max_card_size * max_card_size:
                continue
            
            # Check aspect ratio (credit cards are roughly rectangular)
            aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
            
            # Check if aspect ratio matches credit card (accounting for rotation)
            if abs(aspect_ratio - credit_card_aspect_ratio) < tolerance or \
               abs(aspect_ratio - (1/credit_card_aspect_ratio)) < tolerance:
                
                # Found potential credit card - use it for calibration
                # Use the larger dimension (width or height) for scale calculation
                card_dimension_pixels = max(w, h)
                card_dimension_cm = 8.56  # Credit card width in cm
                
                scale_factor = card_dimension_cm / card_dimension_pixels
                logger.info(f"Credit card detected! Scale factor: {scale_factor:.6f} cm/pixel")
                return scale_factor
        
        return None
    
    def _calculate_scale_factor(self, image: np.ndarray, contours=None) -> float:
        """
        Calculate scale factor to convert pixels to real-world measurements.
        
        Tries multiple methods in order of accuracy:
        1. Automatic credit card detection (if present) - BEST ACCURACY
        2. Smart estimation based on image resolution
        
        Args:
            image: Input image
            contours: Optional list of contours for reference object detection
            
        Returns:
            Scale factor (cm per pixel)
        """
        height, width = image.shape[:2]
        
        # Method 1: Try to detect credit card for automatic calibration
        if contours is not None:
            card_scale = self._detect_credit_card(image, contours)
            if card_scale is not None:
                return card_scale
        
        # Method 2: Improved heuristic based on detected package size
        # If we have package dimensions, estimate scale based on typical package sizes
        # Most shipping boxes are between 10-50cm in their largest dimension
        # We'll use a smarter estimate based on image resolution
        
        # Estimate based on image resolution and typical camera setups
        # Smartphone cameras at 1-2m distance typically see 60-120cm field of view
        # Higher resolution = closer camera = smaller field of view
        
        image_megapixels = (width * height) / 1_000_000
        
        # Adjust field of view estimate based on image resolution
        if image_megapixels > 8:  # High-res camera (close up)
            estimated_fov = 60.0  # Smaller field of view
        elif image_megapixels > 2:  # Medium-res (normal distance)
            estimated_fov = 80.0
        else:  # Lower-res (farther away)
            estimated_fov = 120.0
        
        # Use configurable field of view if set, otherwise use smart estimate
        fov = self.field_of_view_cm if self.field_of_view_cm != 100.0 else estimated_fov
        
        scale_factor = fov / max(width, height)
        
        logger.info(f"Scale factor: {scale_factor:.6f} cm/pixel (Estimated FOV: {fov}cm, Image: {width}x{height}px, {image_megapixels:.1f}MP)")
        
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
