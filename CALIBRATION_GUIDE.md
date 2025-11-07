# 📏 Calibration Guide for Accurate Measurements

## Why Calibration is Important

The accuracy of measurements depends on knowing the **scale factor** - how many centimeters each pixel represents. Currently, the system estimates this, but you can calibrate it for much better accuracy.

## Quick Calibration Method

### Step 1: Take a Test Photo

1. Place a **known-size object** next to your package (e.g., a credit card, ruler, or standard sheet of paper)
2. Take a photo that includes both the package and the reference object
3. Measure the reference object in the photo (in pixels) using image editing software

### Step 2: Calculate Your Field of View

**Formula:**
```
Field of View (cm) = (Reference Object Real Size in cm) × (Image Width in pixels) / (Reference Object Width in pixels)
```

**Example:**
- Credit card real size: 8.56 cm wide
- Credit card in photo: 200 pixels wide
- Image width: 2000 pixels
- Field of View = 8.56 × (2000 / 200) = **85.6 cm**

### Step 3: Set Environment Variable

In Railway dashboard → Your service → Variables, add:

```bash
FIELD_OF_VIEW_CM=85.6
```

Or in your `.env` file:
```bash
FIELD_OF_VIEW_CM=85.6
```

## Advanced Calibration

### Method 1: Use a Ruler

1. Place a ruler next to the package
2. Take photo
3. Count pixels for 10cm on the ruler
4. Calculate: `FIELD_OF_VIEW_CM = 10 × (image_width / ruler_10cm_in_pixels)`

### Method 2: Known Package Size

1. Measure a package manually
2. Upload photo of that package
3. Check what the app measures
4. Adjust `FIELD_OF_VIEW_CM` until measurements match

**Formula:**
```
New FIELD_OF_VIEW_CM = Current FIELD_OF_VIEW_CM × (Actual Size / Measured Size)
```

### Method 3: Camera Distance Method

If you know your camera distance and angle:

```
Field of View ≈ 2 × distance × tan(field_of_view_angle / 2)
```

## Depth Estimation Adjustment

The depth (third dimension) is estimated as a percentage of the smallest visible dimension. You can adjust this:

```bash
DEPTH_ESTIMATION_FACTOR=0.8
```

**Common values:**
- `0.6` - For flat packages (envelopes, thin boxes)
- `0.8` - For typical boxes (default)
- `1.0` - For cube-shaped packages

## Testing Your Calibration

1. Measure a package manually
2. Upload photo with your calibration settings
3. Compare results
4. Adjust `FIELD_OF_VIEW_CM` if needed

## Recommended Setup for Best Accuracy

1. **Fixed Camera Position**: Use same distance/angle for all photos
2. **Good Lighting**: Ensure clear package edges
3. **Reference Object**: Include a credit card or ruler in photos
4. **Calibrate Once**: Set `FIELD_OF_VIEW_CM` based on your setup
5. **Test and Adjust**: Fine-tune based on real measurements

## Current Limitations

- **Single Viewpoint**: Can't measure true depth from one photo
- **Perspective**: Assumes camera is perpendicular to package
- **Shape Assumptions**: Works best for rectangular packages

## Future Improvements

- Automatic reference object detection (credit card, ruler)
- Multiple photo angles for true depth measurement
- Camera calibration system
- Machine learning for better shape recognition

