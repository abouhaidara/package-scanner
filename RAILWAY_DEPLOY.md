# 🚂 Railway Deployment Guide

Complete step-by-step guide to deploy your Package Volume Scanner to Railway.

## Prerequisites

- GitHub account with your `package-scanner` repository
- Railway account (sign up at [railway.app](https://railway.app))

## Step 1: Sign Up for Railway

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign up with GitHub (recommended) or email
4. Authorize Railway to access your GitHub repositories

## Step 2: Deploy from GitHub

1. In Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select your `package-scanner` repository
4. Click **"Deploy Now"**

Railway will automatically:
- ✅ Detect your `Dockerfile`
- ✅ Read `railway.json` configuration
- ✅ Build your Docker container
- ✅ Deploy your application

## Step 3: Configure Environment Variables

After deployment starts, configure environment variables:

1. In your Railway project, click on your **service**
2. Go to **"Variables"** tab
3. Click **"New Variable"** and add:

### Required Variables:

```bash
DEBUG=False
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Optional: Google Cloud Storage

If you want cloud storage (optional):

```bash
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/app/gcloud-credentials.json
```

For Google Cloud Storage on Railway:
1. Upload your service account JSON to Railway
2. Railway will provide a path - use that for `GOOGLE_APPLICATION_CREDENTIALS`

## Step 4: Set Up Custom Domain (Optional)

1. In Railway, go to your service → **"Settings"**
2. Click **"Generate Domain"** for a Railway domain
3. Or click **"Custom Domain"** to use your own domain
4. Follow DNS instructions if using custom domain

## Step 5: Verify Deployment

1. Wait for deployment to complete (usually 2-5 minutes)
2. Railway will show you the deployment URL
3. Visit: `https://your-app.railway.app`
4. Test the health endpoint: `https://your-app.railway.app/health`

## Step 6: Test Your Application

1. **Upload an image** via the web interface
2. **Check the API**: `POST https://your-app.railway.app/api/scan`
3. **View health status**: `GET https://your-app.railway.app/health`

## Troubleshooting

### Build Fails

**Error:** "Cannot find Dockerfile"
- ✅ Make sure `Dockerfile` is in root directory
- ✅ Commit and push `Dockerfile` to GitHub

**Error:** "Failed to install dependencies"
- ✅ Check `requirements.txt` is correct
- ✅ Verify Python version compatibility

### App Crashes

**Check logs:**
1. Railway dashboard → Your service → **"Deployments"**
2. Click on latest deployment → **"View Logs"**
3. Look for error messages

**Common issues:**
- Port mismatch: Railway provides `$PORT` env variable (automatically handled)
- Missing environment variables: Add required vars in "Variables" tab
- Memory issues: Upgrade Railway plan if needed

### OpenCV Errors

If you see OpenCV errors, check:
- ✅ Dockerfile installs required system libraries (already configured)
- ✅ All dependencies are in `requirements.txt`

## Railway Features

### Auto-Deploy

Railway automatically deploys when you push to GitHub:
1. Push to `main` branch → Auto-deploy triggered
2. Railway builds new Docker image
3. Zero-downtime deployment

### Environment Management

- **Development**: Push to `dev` branch (create separate Railway service)
- **Production**: Push to `main` branch

### Monitoring

- View real-time logs in Railway dashboard
- Set up alerts for errors
- Monitor resource usage

## Cost

**Free Tier:**
- $5 credit per month
- Enough for small apps
- Sleeps after 5 minutes of inactivity (wakes on request)

**Paid Plans:**
- $5/month: Always-on, more resources
- $10/month: Better performance

## Next Steps

1. ✅ Your app is deployed!
2. Set up Google Cloud Storage (optional)
3. Configure custom domain (optional)
4. Monitor usage in Railway dashboard

## Quick Commands

### Check Deployment Status
```bash
# In Railway dashboard, or use Railway CLI
railway status
```

### View Logs
```bash
railway logs
```

### Update App
```bash
# Just push to GitHub - Railway auto-deploys!
git add .
git commit -m "Update app"
git push
```

## Need Help?

- Railway Docs: https://docs.railway.app
- Support: https://railway.app/discord
- Your app logs: Railway dashboard → Service → Logs

🎉 **Your Package Volume Scanner is now live on Railway!**

