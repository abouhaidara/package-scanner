# ☁️ Google Cloud Storage Setup Guide

This guide will help you set up Google Cloud Storage for your Package Volume Scanner.

## 📋 Prerequisites

- A Google account
- Access to Google Cloud Console (https://console.cloud.google.com)

## 🚀 Step-by-Step Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "package-scanner")
5. Click "Create"
6. Note your **Project ID** (different from project name)

### Step 2: Enable Cloud Storage API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Cloud Storage API"
3. Click on it and click "Enable"

### Step 3: Create a Cloud Storage Bucket

1. Go to "Cloud Storage" > "Buckets" in the left sidebar
2. Click "Create Bucket"
3. Choose a unique bucket name (e.g., "package-scanner-images")
4. Select a location (choose closest to you)
5. Choose storage class: "Standard"
6. Click "Create"
7. Note your **Bucket Name**

### Step 4: Create a Service Account

1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Enter a name: "package-scanner-service"
4. Enter description: "Service account for package scanner"
5. Click "Create and Continue"
6. Grant role: "Storage Admin" (or "Storage Object Admin" for more restricted access)
7. Click "Continue" then "Done"

### Step 5: Create and Download Service Account Key

1. Click on the service account you just created
2. Go to the "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" format
5. Click "Create"
6. The JSON file will download automatically

### Step 6: Configure Your Application

1. **Move the downloaded JSON file** to your project directory:
   ```bash
   mv ~/Downloads/your-project-*.json /Users/abouhaidara/package_scanner/gcloud-credentials.json
   ```

2. **Update your `.env` file** with your credentials:
   ```bash
   cd /Users/abouhaidara/package_scanner
   nano .env
   ```
   
   Update these lines:
   ```env
   GOOGLE_CLOUD_PROJECT_ID=your-project-id-here
   GOOGLE_CLOUD_BUCKET_NAME=your-bucket-name-here
   GOOGLE_APPLICATION_CREDENTIALS=/Users/abouhaidara/package_scanner/gcloud-credentials.json
   ```

3. **Secure your credentials file**:
   ```bash
   chmod 600 gcloud-credentials.json
   ```

### Step 7: Test the Configuration

Test your setup:
```bash
cd /Users/abouhaidara/package_scanner
python3 test_my_image.py uploads/Screenshot\ 2025-10-28\ at\ 1.11.38\ AM.jpg
```

If configured correctly, you should see:
```
☁️ CLOUD STORAGE:
   URL: https://storage.googleapis.com/your-bucket/packages/...
```

## 🔒 Security Best Practices

1. **Never commit credentials to git**: Add to `.gitignore`:
   ```
   .env
   *-credentials.json
   gcloud-credentials.json
   ```

2. **Use environment-specific credentials**: Different credentials for dev/staging/production

3. **Rotate keys regularly**: Update service account keys periodically

4. **Restrict permissions**: Only grant necessary permissions (Storage Object Admin instead of Storage Admin)

## 🧪 Troubleshooting

### Error: "Could not automatically determine credentials"
- Make sure `GOOGLE_APPLICATION_CREDENTIALS` points to the correct JSON file path
- Verify the JSON file exists and is readable

### Error: "Bucket not found"
- Verify the bucket name matches exactly (case-sensitive)
- Ensure the bucket exists in your project

### Error: "Permission denied"
- Check that your service account has "Storage Object Admin" or "Storage Admin" role
- Verify the service account key hasn't been deleted

### Error: "API not enabled"
- Go to Cloud Console > APIs & Services
- Enable "Cloud Storage API"

## ✅ Verification

To verify everything is working:

1. Check health endpoint:
   ```bash
   curl http://127.0.0.1:5002/health
   ```
   Should show: `"scanner_configured": true`

2. Process an image and check for cloud URL in results

3. Check your Google Cloud Storage bucket - you should see uploaded images in the `packages/` folder

## 📚 Additional Resources

- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)
- [GCS Python Client Library](https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python)

