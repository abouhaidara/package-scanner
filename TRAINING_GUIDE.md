# 📚 Training Data Guide

## Simple Learning System

The app learns from packages with known dimensions to improve accuracy automatically.

## How It Works

1. **You provide training data**: Upload images of packages where you know the exact dimensions
2. **App learns**: The app calculates scale factors from your training examples
3. **Automatic improvement**: Future scans use similar training examples for better accuracy

## Adding Training Data

### Option 1: Web Interface (Easiest)

1. Go to `/train` page (or click "Add Training Data" link)
2. Upload a package image
3. Enter the known dimensions (width, height, depth in inches)
4. Click "Add Training Example"

### Option 2: Command Line

```bash
python add_training_data.py <image_path> <width_inches> <height_inches> <depth_inches>
```

**Example:**
```bash
python add_training_data.py package1.jpg 12.5 8.3 6.2
```

## What Happens

- The app detects the package in the image (pixel dimensions)
- Calculates the scale factor: `actual_size / pixel_size`
- Stores this in `training_data.json`
- Uses it for future similar packages

## Tips for Best Results

1. **Variety**: Add examples with different:
   - Image resolutions (different cameras/phones)
   - Package sizes
   - Package shapes

2. **Accuracy**: Make sure your measurements are accurate (use a ruler/tape measure)

3. **Quantity**: More examples = better accuracy
   - Start with 5-10 examples
   - Add more as you scan packages

## Training Data File

All training data is stored in `training_data.json`. You can:
- View it to see all examples
- Backup it to keep your training data
- Share it across deployments

## How It's Used

When scanning a new package:
1. App finds similar training examples (same image resolution, similar package shape)
2. Uses their scale factors to calculate accurate dimensions
3. Falls back to other methods if no similar examples found

## Example Training Data Format

```json
[
  {
    "image_path": "uploads/train_20250101_120000_package1.jpg",
    "image_width": 1920,
    "image_height": 1080,
    "package_width_pixels": 450,
    "package_height_pixels": 320,
    "package_depth_pixels": 256,
    "actual_width_cm": 31.75,
    "actual_height_cm": 21.08,
    "actual_depth_cm": 15.75,
    "scale_factor": 0.0706,
    "image_megapixels": 2.07
  }
]
```

## That's It!

No complicated setup. Just add a few examples with known dimensions, and the app gets smarter automatically.

