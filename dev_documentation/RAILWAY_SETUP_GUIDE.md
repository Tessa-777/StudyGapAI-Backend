# Railway Deployment Setup Guide

Complete step-by-step guide for deploying StudyGapAI Backend to Railway.

## Step 1: Service Configuration

After connecting your GitHub repository, configure your service:

### Service Settings

1. **Service Name**
   - Name: `studygapai-backend` (or your preferred name)
   - This will be part of your Railway URL

2. **Region**
   - Choose the region closest to your users
   - Recommended: `US West` or `US East` for US users
   - Available regions: US, EU, Asia

3. **Branch**
   - Select your deployment branch (usually `main` or `master`)
   - Railway will auto-deploy on push to this branch

## Step 2: Build Settings

Railway will auto-detect your Python application. Verify these settings:

### Build Configuration

1. **Builder**: `Nixpacks` (auto-detected)
   - Railway will automatically detect Python from `requirements.txt`
   - Python version will be read from `runtime.txt` (3.11.9)

2. **Build Command** (usually auto-detected):
   ```
   pip install --upgrade pip && pip install -r requirements.txt
   ```
   - Railway should auto-detect this
   - If not, add it manually in Settings → Build

3. **Start Command** (from Procfile):
   ```
   gunicorn backend.app:app --workers=2 --timeout=120 --bind 0.0.0.0:$PORT
   ```
   - Railway will automatically use your `Procfile`
   - The `$PORT` variable is set automatically by Railway

### Verify Build Settings

- Go to **Settings** → **Build & Deploy**
- Ensure:
  - ✅ Root Directory: `/` (root of repository)
  - ✅ Build Command: Auto-detected or `pip install --upgrade pip && pip install -r requirements.txt`
  - ✅ Start Command: Auto-detected from `Procfile`

## Step 3: Environment Variables

Go to **Variables** tab and add the following:

### Required Environment Variables

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here-generate-a-strong-one
APP_NAME=StudyGapAI Backend
APP_VERSION=0.1.0

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
USE_IN_MEMORY_DB=false

# Google Gemini AI Configuration
GOOGLE_API_KEY=your-google-api-key-here
AI_MODEL_NAME=gemini-1.5-flash
AI_MOCK=false

# CORS Configuration
CORS_ORIGINS=https://your-frontend-domain.com,http://localhost:5173

# Testing (optional)
TESTING=false
```

### Important Notes:

1. **SECRET_KEY**: Generate a strong secret key:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```
   Or use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

2. **PORT**: Do NOT set this manually - Railway provides it automatically

3. **CORS_ORIGINS**: 
   - Add your frontend domain(s)
   - Separate multiple origins with commas
   - Include `http://localhost:5173` for local development

4. **USE_IN_MEMORY_DB**: Must be `false` for production

5. **AI_MOCK**: Set to `false` for production (uses real Gemini API)

## Step 4: Network Settings

### Port Configuration

- Railway automatically sets the `PORT` environment variable
- Your `Procfile` uses `$PORT` - this is correct
- No manual configuration needed

### Health Checks (Optional)

Railway can check if your app is healthy:

1. Go to **Settings** → **Health Checks**
2. Enable health check
3. Path: `/health`
4. Interval: `30 seconds`

## Step 5: Domain Configuration

### Generate Public URL

1. Go to **Settings** → **Networking**
2. Click **Generate Domain**
3. Railway will create a public URL like: `https://studygapai-backend.up.railway.app`
4. Copy this URL - you'll need it for:
   - Frontend CORS configuration
   - Testing your API

### Custom Domain (Optional)

1. Go to **Settings** → **Networking**
2. Click **Custom Domain**
3. Add your custom domain
4. Configure DNS records as instructed by Railway

## Step 6: Deployment Settings

### Auto-Deploy

1. Go to **Settings** → **Deploy**
2. Ensure **Auto-Deploy** is enabled
3. Railway will automatically deploy on every push to your selected branch

### Manual Deploy

- Click **Deploy** button to manually trigger deployment
- Useful for testing or rolling back

## Step 7: Monitoring & Logs

### View Logs

1. Go to **Deployments** tab
2. Click on a deployment to see build logs
3. Go to **Metrics** tab for runtime logs
4. Real-time logs are available in the Railway dashboard

### Monitor Performance

1. Go to **Metrics** tab
2. View:
   - CPU usage
   - Memory usage
   - Request metrics
   - Error rates

## Step 8: Verify Deployment

### Test Your API

1. **Root Endpoint**:
   ```bash
   curl https://your-project.railway.app/
   ```
   Expected response:
   ```json
   {
     "message": "StudyGapAI Backend API",
     "status": "running",
     "version": "0.1.0",
     "endpoints": {...}
   }
   ```

2. **Health Endpoint**:
   ```bash
   curl https://your-project.railway.app/health
   ```
   Expected response:
   ```json
   {
     "status": "ok",
     "version": "0.1.0"
   }
   ```

3. **API Endpoint**:
   ```bash
   curl https://your-project.railway.app/api/users/register \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "name": "Test User", "password": "test123"}'
   ```

## Step 9: Update Frontend

Update your frontend to use the Railway backend URL:

```javascript
// In your frontend code
const API_URL = 'https://your-project.railway.app';
```

Update CORS_ORIGINS in Railway to include your frontend domain.

## Troubleshooting

### Build Fails

**Issue**: Build fails with dependency errors
**Solution**:
- Check `requirements.txt` is correct
- Verify Python version in `runtime.txt` (3.11.9)
- Check build logs in Railway dashboard

### App Won't Start

**Issue**: Service crashes on startup
**Solution**:
- Check that `Procfile` is correct
- Verify `backend.app:app` path is correct
- Check environment variables are set
- View logs in Railway dashboard

### Port Errors

**Issue**: Port binding errors
**Solution**:
- Ensure `Procfile` uses `$PORT` (not hardcoded port)
- Railway sets PORT automatically - don't override it
- Check that host is `0.0.0.0` (not `127.0.0.1`)

### Environment Variables Not Working

**Issue**: App uses default values
**Solution**:
- Verify variables are set in Railway Variables tab
- Check variable names are exact (case-sensitive)
- Redeploy after changing variables
- Restart service if needed

### Database Connection Errors

**Issue**: Can't connect to Supabase
**Solution**:
- Verify `SUPABASE_URL` is correct
- Check `SUPABASE_SERVICE_ROLE_KEY` is set (not just anon key)
- Ensure `USE_IN_MEMORY_DB=false`
- Check Supabase project is active
- Verify network connectivity from Railway to Supabase

### CORS Errors

**Issue**: Frontend can't make requests
**Solution**:
- Verify `CORS_ORIGINS` includes your frontend domain
- Check frontend is using correct backend URL
- Ensure CORS is configured in `backend/app.py`
- Redeploy after changing CORS_ORIGINS

## Quick Reference

### Railway Dashboard Tabs

- **Deployments**: View deployment history and logs
- **Metrics**: Monitor performance and resources
- **Variables**: Manage environment variables
- **Settings**: Configure service settings
- **Networking**: Manage domains and ports

### Important Files

- `Procfile`: Defines how to start the app
- `requirements.txt`: Python dependencies
- `runtime.txt`: Python version
- `Dockerfile`: Alternative deployment method
- `nixpacks.toml`: Nixpacks configuration

### Railway URLs

- Dashboard: https://railway.app
- Your Service: https://your-project.railway.app (after deployment)
- Documentation: https://docs.railway.app

## Next Steps

1. ✅ Set all environment variables
2. ✅ Verify build settings
3. ✅ Deploy and test
4. ✅ Update frontend with Railway URL
5. ✅ Monitor logs and metrics
6. ✅ Set up custom domain (optional)
7. ✅ Configure health checks (optional)

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app

---

**Last Updated**: 2025-01-09

