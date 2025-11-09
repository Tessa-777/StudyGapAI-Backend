# Vercel Deployment Guide for StudyGapAI Backend

This guide will help you deploy your Flask backend to Vercel as a serverless function.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Environment Variables](#environment-variables)
4. [Deployment Steps](#deployment-steps)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Important Notes](#important-notes)

---

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional, for local testing):
   ```bash
   npm install -g vercel
   ```
3. **GitHub Repository**: Your code should be in a GitHub repository
4. **Environment Variables**: Have all your environment variables ready (see below)

---

## Project Structure

The project is structured as follows for Vercel deployment:

```
Royal-Light-StudyGapAI/
├── api/
│   └── index.py          # Vercel serverless function entry point
├── backend/
│   ├── app.py            # Flask application
│   ├── config.py         # Configuration
│   ├── routes/           # API routes
│   ├── services/         # Business logic
│   ├── utils/            # Utilities
│   └── repositories/     # Data access layer
├── vercel.json           # Vercel configuration
├── .vercelignore         # Files to exclude from deployment
├── requirements.txt      # Python dependencies
└── README.md
```

---

## Environment Variables

Set these environment variables in the Vercel Dashboard (Project Settings → Environment Variables):

### Required Variables

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here  # Generate a strong random string

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key  # For backend operations

# Database Configuration
USE_IN_MEMORY_DB=false  # Must be false for production

# AI Configuration
GOOGLE_API_KEY=your-google-api-key
AI_MODEL_NAME=gemini-1.5-flash  # or gemini-2.0-flash-exp
AI_MOCK=false  # Set to false for production (uses real Gemini API)

# CORS Configuration
CORS_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:5173
# Or set to "*" to allow all origins (not recommended for production)
```

### Optional Variables

```bash
APP_NAME=StudyGapAI Backend
APP_VERSION=0.1.0
TESTING=false
```

### Generating SECRET_KEY

Generate a secure secret key:

```python
import secrets
print(secrets.token_urlsafe(32))
```

Copy the output and use it as your `SECRET_KEY` value.

---

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Configure for Vercel deployment"
   git push origin main
   ```

2. **Import Project in Vercel**
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click **"Add New Project"**
   - Import your GitHub repository
   - Vercel will auto-detect it as a Python project

3. **Configure Project Settings**
   - **Framework Preset**: Other (or leave as auto-detected)
   - **Root Directory**: `./` (root of repository)
   - **Build Command**: Leave empty (Vercel handles this)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

4. **Add Environment Variables**
   - Go to **Settings → Environment Variables**
   - Add all environment variables listed above
   - Make sure to set them for **Production**, **Preview**, and **Development** environments as needed

5. **Deploy**
   - Click **"Deploy"**
   - Wait for the build to complete
   - Your app will be live at `https://your-project.vercel.app`

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI** (if not already installed)
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```
   
   Follow the prompts:
   - Link to existing project or create new one
   - Confirm project settings
   - Environment variables will be prompted

4. **Deploy to Production**
   ```bash
   vercel --prod
   ```

---

## Verification

After deployment, verify your API is working:

### 1. Test Root Endpoint

```bash
curl https://your-project.vercel.app/
```

Expected response:
```json
{
  "message": "StudyGapAI Backend API",
  "status": "running",
  "version": "0.1.0",
  "endpoints": {
    "health": "/health",
    "users": "/api/users",
    "quiz": "/api/quiz",
    "ai": "/api/ai",
    "progress": "/api/progress",
    "analytics": "/api/analytics",
    "resources": "/api/resources"
  }
}
```

### 2. Test Health Endpoint

```bash
curl https://your-project.vercel.app/health
```

Expected response:
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### 3. Test API Endpoint

```bash
curl https://your-project.vercel.app/api/users/register \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test User", "password": "test123"}'
```

### 4. Check Logs

- Go to Vercel Dashboard → Your Project → **Logs** tab
- Check for any errors or warnings
- Look for successful requests

---

## Troubleshooting

### Issue: 404 Not Found

**Symptoms**: All routes return 404

**Solutions**:
1. Check that `api/index.py` exists and exports the `app` instance
2. Verify `vercel.json` routes configuration
3. Check Vercel build logs for errors
4. Ensure `backend/app.py` is properly importing and creating the Flask app

### Issue: Import Errors

**Symptoms**: Build fails with `ModuleNotFoundError`

**Solutions**:
1. Verify `requirements.txt` includes all dependencies
2. Check that `api/index.py` properly adds project root to `sys.path`
3. Ensure all Python files have proper imports
4. Check Vercel build logs for specific import errors

### Issue: Environment Variables Not Working

**Symptoms**: App uses default values instead of environment variables

**Solutions**:
1. Verify environment variables are set in Vercel Dashboard
2. Check that variables are set for the correct environment (Production/Preview/Development)
3. Redeploy after adding/changing environment variables
4. Check variable names match exactly (case-sensitive)

### Issue: CORS Errors

**Symptoms**: Frontend can't make requests due to CORS

**Solutions**:
1. Verify `CORS_ORIGINS` includes your frontend domain
2. Check that CORS is configured for all routes (not just `/api/*`)
3. Ensure frontend is using the correct backend URL
4. Check browser console for specific CORS error messages

### Issue: Database Connection Errors

**Symptoms**: Errors connecting to Supabase

**Solutions**:
1. Verify `SUPABASE_URL` is correct
2. Check `SUPABASE_SERVICE_ROLE_KEY` is set (not just anon key)
3. Ensure `USE_IN_MEMORY_DB=false` in production
4. Check Supabase project is active and accessible
5. Verify network connectivity from Vercel to Supabase

### Issue: Cold Starts (Slow First Request)

**Symptoms**: First request after inactivity is very slow

**Solutions**:
1. This is normal for serverless functions
2. Consider using Vercel Pro plan for better cold start performance
3. Implement health check pings to keep functions warm
4. Optimize imports and reduce startup time

### Issue: Function Timeout

**Symptoms**: Requests timeout after 10 seconds (Hobby plan) or 60 seconds (Pro plan)

**Solutions**:
1. Optimize long-running operations (e.g., AI API calls)
2. Consider upgrading to Vercel Pro for longer timeouts
3. Implement async processing for heavy tasks
4. Break down large operations into smaller chunks

---

## Important Notes

### Serverless Limitations

1. **State**: Serverless functions are stateless. In-memory cache will reset on each invocation.
2. **Cold Starts**: First request after inactivity may be slower (1-2 seconds).
3. **Timeouts**: 
   - Hobby plan: 10 seconds
   - Pro plan: 60 seconds
   - Enterprise: Custom
4. **File System**: Read-only except `/tmp` directory (512 MB limit).

### Best Practices

1. **Environment Variables**: Never commit secrets. Use Vercel Dashboard for environment variables.
2. **Database**: Always use Supabase (external database) in production. Don't rely on in-memory storage.
3. **Caching**: Use external cache (Redis) for production. In-memory cache won't persist.
4. **Logging**: Use Vercel's logging dashboard. Logs are automatically collected.
5. **Monitoring**: Set up Vercel Analytics to monitor performance and errors.

### Cost Considerations

- **Hobby Plan**: Free, but limited to 10-second function timeouts
- **Pro Plan**: $20/month, 60-second timeouts, better performance
- **Bandwidth**: Generous free tier, pay for overage
- **Function Invocations**: Generous free tier on both plans

### Performance Optimization

1. **Reduce Cold Starts**: 
   - Minimize imports
   - Lazy load heavy dependencies
   - Keep functions warm with health checks

2. **Optimize Response Times**:
   - Use database connection pooling
   - Implement caching where appropriate
   - Optimize AI API calls

3. **Monitor Performance**:
   - Use Vercel Analytics
   - Check function execution times in logs
   - Monitor error rates

---

## Next Steps

1. **Set Up Custom Domain** (optional):
   - Go to Project Settings → Domains
   - Add your custom domain
   - Configure DNS settings

2. **Set Up Monitoring**:
   - Enable Vercel Analytics
   - Set up error tracking (e.g., Sentry)
   - Configure alerts

3. **Update Frontend**:
   - Update frontend to use new Vercel backend URL
   - Update CORS_ORIGINS to include frontend domain
   - Test all API endpoints

4. **CI/CD**:
   - Vercel automatically deploys on git push
   - Set up preview deployments for PRs
   - Configure production deployments for main branch

---

## Support

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Flask on Vercel**: [vercel.com/docs/frameworks/backend/flask](https://vercel.com/docs/frameworks/backend/flask)
- **Vercel Support**: [vercel.com/support](https://vercel.com/support)

---

## Quick Reference

### Deployment Commands

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs

# List deployments
vercel list
```

### Environment Variables Template

```bash
FLASK_ENV=production
SECRET_KEY=<generate-secure-key>
SUPABASE_URL=<your-supabase-url>
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
USE_IN_MEMORY_DB=false
GOOGLE_API_KEY=<your-google-api-key>
AI_MODEL_NAME=gemini-1.5-flash
AI_MOCK=false
CORS_ORIGINS=<your-frontend-url>
```

---

**Last Updated**: 2025-01-09

