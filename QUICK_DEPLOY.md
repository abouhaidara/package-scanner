# 🚀 Quick Deployment Guide

## ⚠️ Important: Vercel Limitation

**Vercel does NOT support OpenCV** - Your app requires computer vision libraries that need system dependencies.

Use one of these platforms instead:

## Option 1: Railway (Easiest - 5 minutes) ⭐

1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `package-scanner` repository
4. Railway auto-detects your `Dockerfile` and `railway.json`
5. Click "Deploy" - done! 🎉

Your app will be live at: `https://your-app.railway.app`

## Option 2: Render (Free tier available)

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select `package-scanner`
5. Settings:
   - **Environment**: Docker
   - **Build Command**: (auto-detected from Dockerfile)
   - **Start Command**: (auto-detected)
6. Click "Create Web Service"

## Option 3: Google Cloud Run (Already configured!)

You already have deployment scripts! Just run:

```bash
cd /Users/abouhaidara/package_scanner
python3 deploy_helper.py
# Select option 5: Google Cloud Run
```

## Option 4: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# In your project directory
fly launch

# Follow prompts:
# - Select Dockerfile
# - Choose a region
# - App name: package-scanner
```

## Environment Variables

Don't forget to set these in your deployment platform:

- `DEBUG=False`
- `PORT=8000` (or use platform's PORT variable)
- `GOOGLE_CLOUD_PROJECT_ID` (if using cloud storage)
- `GOOGLE_CLOUD_BUCKET_NAME` (if using cloud storage)
- `GOOGLE_APPLICATION_CREDENTIALS` (if using cloud storage)

## Recommended: Railway

✅ Easiest setup  
✅ GitHub integration  
✅ Auto-deploy on push  
✅ Free tier available  
✅ Full Docker support (OpenCV works!)

## Need Help?

See `VERCEL_DEPLOYMENT.md` for detailed explanations and troubleshooting.

