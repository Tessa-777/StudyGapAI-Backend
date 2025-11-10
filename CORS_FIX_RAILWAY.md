# CORS Fix for Railway + Vercel Deployment

## Problem
Frontend on Vercel (`https://royal-light-study-gap-ai.vercel.app`) cannot connect to backend on Railway due to:
1. Frontend using `localhost:5000` instead of Railway URL
2. Backend CORS not allowing Vercel domain

## Solution

### Step 1: Set CORS_ORIGINS in Railway

1. Go to your Railway project dashboard
2. Click on your service
3. Go to **Variables** tab
4. Find or add `CORS_ORIGINS` variable
5. Set the value to:
   ```
   https://royal-light-study-gap-ai.vercel.app,http://localhost:5173
   ```
6. Click **Save** or **Add Variable**
7. Railway will automatically redeploy with the new variable

**Important**: Make sure there are NO spaces around the comma, and include both:
- Your Vercel production URL: `https://royal-light-study-gap-ai.vercel.app`
- Local development URL: `http://localhost:5173` (for local testing)

### Step 2: Get Your Railway Backend URL

1. Go to Railway dashboard
2. Click on your service
3. Go to **Settings** → **Networking**
4. Copy your Railway URL (e.g., `https://studygapai-backend.up.railway.app`)
5. Save this URL - you'll need it for the frontend

### Step 3: Set Frontend API URL in Vercel

1. Go to your Vercel project dashboard
2. Click on your project: `royal-light-study-gap-ai`
3. Go to **Settings** → **Environment Variables**
4. Find or add `VITE_API_BASE_URL` variable
5. Set the value to your Railway URL (from Step 2):
   ```
   https://studygapai-backend.up.railway.app/api
   ```
   **Important**: Include `/api` at the end
6. Make sure it's set for:
   - ✅ Production
   - ✅ Preview
   - ✅ Development (optional, or use `http://localhost:5000/api` for local dev)
7. Click **Save**

### Step 4: Redeploy Frontend

After setting the environment variable:

1. Go to **Deployments** tab in Vercel
2. Click the **...** menu on the latest deployment
3. Click **Redeploy**
4. Or push a new commit to trigger automatic redeploy
5. Wait for deployment to complete

### Step 5: Verify the Fix

1. **Check Railway CORS_ORIGINS**:
   - Railway Variables tab should have:
     ```
     CORS_ORIGINS=https://royal-light-study-gap-ai.vercel.app,http://localhost:5173
     ```

2. **Check Vercel VITE_API_BASE_URL**:
   - Vercel Environment Variables should have:
     ```
     VITE_API_BASE_URL=https://your-railway-url.up.railway.app/api
     ```

3. **Test the Connection**:
   - Open your Vercel app: `https://royal-light-study-gap-ai.vercel.app`
   - Open browser DevTools → Network tab
   - Try to use the app (e.g., load quiz questions)
   - Check that requests go to Railway URL, not localhost
   - Check that there are no CORS errors

## Troubleshooting

### Still Getting CORS Errors?

1. **Verify Railway CORS_ORIGINS**:
   - Make sure the exact Vercel URL is in the list
   - Check for typos (https vs http, trailing slashes)
   - Ensure no extra spaces

2. **Check Railway Logs**:
   - Go to Railway → Metrics tab
   - Look for CORS-related errors
   - Check if requests are reaching the backend

3. **Verify Frontend API URL**:
   - Open browser DevTools → Console
   - Check what URL the frontend is using
   - Should be Railway URL, not localhost

4. **Clear Browser Cache**:
   - Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Or clear browser cache completely

### Frontend Still Using localhost?

1. **Check Vercel Environment Variables**:
   - Make sure `VITE_API_BASE_URL` is set correctly
   - Make sure it's set for **Production** environment
   - Redeploy after changing variables

2. **Check Frontend Code**:
   - Make sure frontend uses `import.meta.env.VITE_API_BASE_URL`
   - Not hardcoded `localhost:5000`

3. **Rebuild Frontend**:
   - Environment variables are baked into the build
   - Must rebuild/redeploy after changing them

### Backend Not Receiving Requests?

1. **Check Railway Service Status**:
   - Make sure service is running (not sleeping)
   - Check deployment logs for errors

2. **Test Railway URL Directly**:
   ```bash
   curl https://your-railway-url.up.railway.app/health
   ```
   Should return: `{"status": "ok", "version": "0.1.0"}`

3. **Check Railway Networking**:
   - Make sure public URL is generated
   - Check that port is correctly configured

## Quick Checklist

- [ ] Railway `CORS_ORIGINS` includes Vercel URL
- [ ] Railway `CORS_ORIGINS` includes `http://localhost:5173`
- [ ] Vercel `VITE_API_BASE_URL` set to Railway URL + `/api`
- [ ] Vercel environment variable set for Production
- [ ] Frontend redeployed after setting variables
- [ ] Railway service is running
- [ ] Tested connection in browser DevTools

## Environment Variables Summary

### Railway (Backend)
```
CORS_ORIGINS=https://royal-light-study-gap-ai.vercel.app,http://localhost:5173
```

### Vercel (Frontend)
```
VITE_API_BASE_URL=https://your-railway-url.up.railway.app/api
```

## Still Having Issues?

1. Check Railway logs for CORS errors
2. Check Vercel build logs for environment variable issues
3. Test Railway URL directly with curl
4. Verify both services are deployed and running
5. Check browser console for specific error messages

---

**Last Updated**: 2025-01-09

