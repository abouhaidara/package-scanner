# 🔧 Railway Troubleshooting Guide

## Common Railway Deployment Issues

### Issue 1: "Port binding failed" or "Address already in use"

**Solution:**
- Railway automatically provides `$PORT` environment variable
- The `railway.json` startCommand uses `$PORT` correctly
- Make sure you're not hardcoding port numbers

**Fixed in latest commit:** ✅ Dockerfile now uses Railway's `$PORT` properly

### Issue 2: "Cannot find module" or Import Errors

**Solution:**
1. Check that all dependencies are in `requirements.txt`
2. Verify `gunicorn` is installed (now added to requirements.txt)
3. Railway should auto-install from `requirements.txt`

### Issue 3: "Build timeout" or "Build failed"

**Possible causes:**
- OpenCV installation takes time (this is normal - 2-5 minutes)
- System libraries need to be installed (already in Dockerfile)

**Solution:**
- Wait for build to complete (can take up to 5 minutes)
- Check Railway logs for specific error messages

### Issue 4: "Health check failed"

**Solution:**
- Health check uses port 8000 by default
- Railway overrides this with `$PORT` at runtime
- The health endpoint should be: `/health`

**Test health endpoint:**
```bash
curl https://your-app.railway.app/health
```

### Issue 5: "Dockerfile build error"

**Common fixes:**
- ✅ Fixed: EXPOSE now uses static port 8000
- ✅ Fixed: HEALTHCHECK uses static port
- ✅ Fixed: CMD updated for Railway compatibility

## Railway-Specific Settings

### Environment Variables Required:

```bash
DEBUG=False
FLASK_ENV=production
SECRET_KEY=<your-secret-key>
```

**Note:** Railway automatically sets `PORT` - don't set it manually!

### Start Command:

Railway uses the `startCommand` from `railway.json`:
```json
"startCommand": "gunicorn -w 2 -b 0.0.0.0:$PORT --timeout 120 --keep-alive 2 app:app"
```

This:
- Uses 2 workers (reduced from 4 for Railway's free tier)
- Binds to `$PORT` (Railway's dynamic port)
- Uses your Flask app: `app:app`

## Quick Fixes

### If deployment fails:

1. **Check Railway logs:**
   - Go to Railway dashboard
   - Click on your service
   - View "Logs" tab

2. **Verify files are pushed:**
   ```bash
   git status
   git push origin main
   ```

3. **Restart deployment:**
   - In Railway dashboard
   - Click "Redeploy"

4. **Check environment variables:**
   - Variables tab → Make sure required vars are set

## Still Having Issues?

### Debug Steps:

1. **Check build logs** in Railway dashboard
2. **Verify Dockerfile syntax** (recently fixed)
3. **Test locally** (if Docker available):
   ```bash
   docker build -t test-app .
   docker run -p 8000:8000 -e PORT=8000 test-app
   ```

4. **Check Railway status:**
   - Railway dashboard → Service status
   - Look for error messages

### Get Help:

- Railway Discord: https://railway.app/discord
- Railway Docs: https://docs.railway.app
- Check GitHub issues for similar problems

## Recent Fixes Applied ✅

1. ✅ Removed `PORT=${PORT:-8000}` from Dockerfile ENV (Railway sets it)
2. ✅ Fixed EXPOSE to use static port 8000
3. ✅ Fixed HEALTHCHECK port
4. ✅ Updated railway.json startCommand
5. ✅ Added gunicorn to requirements.txt

**These fixes should resolve Railway deployment issues!**

