# 📏 Accuracy Improvement Guide

## Automatic Calibration (No Setup Required!)

The app now automatically improves accuracy in three ways:

### 1. **Automatic Credit Card Detection** ⭐ (Easiest)

**How it works:**
- Simply place a credit card next to your package in the photo
- The app automatically detects it and uses it for calibration
- **No user input needed!**

**Why it works:**
- Credit cards have a standard size (8.56cm × 5.398cm)
- The app recognizes the credit card shape and uses it to calculate accurate measurements

**Best for:** Most accurate results with zero effort

---

### 2. **Optional: Enter One Known Dimension** (Simple)

**How it works:**
- After selecting an image, an optional field appears
- Enter one dimension you know (width or height) in inches
- The app uses this to calibrate all other measurements

**Example:**
- You know the package width is 12 inches
- Enter "12" and select "Width"
- The app calculates accurate height and depth automatically

**Best for:** When you know one dimension but want accurate results

---

### 3. **Smart Automatic Estimation** (Default)

**How it works:**
- The app automatically estimates scale based on image resolution
- Higher resolution photos = better accuracy
- No user input needed

**Best for:** Quick scans when you don't have a reference object

---

## Tips for Best Accuracy

1. **Use a Credit Card** - Place it next to the package for automatic calibration
2. **Good Lighting** - Ensure clear package edges are visible
3. **Straight-On Photo** - Take photo perpendicular to the package (not at an angle)
4. **Clear Background** - Place package on contrasting background for better edge detection

---

## Advanced: Manual Calibration (Optional)

If you want to fine-tune for a specific camera setup, you can set environment variables:

### Field of View Calibration

```bash
FIELD_OF_VIEW_CM=80.0
```

**How to find your value:**
1. Take a photo with a credit card
2. If measurements are too small, increase the value
3. If measurements are too large, decrease the value

### Depth Estimation Factor

```bash
DEPTH_ESTIMATION_FACTOR=0.8
```

**Common values:**
- `0.6` - For flat packages (envelopes, thin boxes)
- `0.8` - For typical boxes (default)
- `1.0` - For cube-shaped packages

---

## Current Limitations

- **Single Viewpoint**: Can't measure true depth from one photo (estimated)
- **Perspective**: Works best when camera is perpendicular to package
- **Shape Assumptions**: Works best for rectangular packages

---

## Future Improvements

- Multiple photo angles for true depth measurement
- Machine learning for better shape recognition
- Support for irregular package shapes
