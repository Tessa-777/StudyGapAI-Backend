# Vercel Deployment Quick Start

## 🚀 Quick Deployment Steps

### 1. Prerequisites
- ✅ Code pushed to GitHub
- ✅ Vercel account created
- ✅ Environment variables ready

### 2. Deploy to Vercel

#### Option A: Via Dashboard (Easiest)
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Click **"Deploy"** (Vercel auto-detects Python/Flask)

#### Option B: Via CLI
```bash
npm install -g vercel
vercel login
vercel --prod
```

### 3. Configure Environment Variables

In Vercel Dashboard → Project Settings → Environment Variables, add:

```bash
# Required
FLASK_ENV=production
SECRET_KEY=<generate-with: python -c "import secrets; print(secrets.token_urlsafe(32))">
SUPABASE_URL=<your-supabase-url>
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
USE_IN_MEMORY_DB=false
GOOGLE_API_KEY=<your-google-api-key>
AI_MODEL_NAME=gemini-1.5-flash
AI_MOCK=false
CORS_ORIGINS=<your-frontend-url>
```

### 4. Verify Deployment

```bash
# Test root endpoint
curl https://your-project.vercel.app/

# Test health endpoint
curl https://your-project.vercel.app/health
```

### 5. Update Frontend

Update your frontend to use the new Vercel backend URL:
```javascript
const API_URL = 'https://your-project.vercel.app';
```

---

## 📋 Checklist

- [ ] Code pushed to GitHub
- [ ] Vercel project created
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] Root endpoint returns 200
- [ ] Health endpoint returns 200
- [ ] API endpoints working
- [ ] Frontend updated with new URL
- [ ] CORS configured correctly

---

## 🔍 Troubleshooting

### 404 Errors
- Check `api/index.py` exists and exports `app`
- Verify `vercel.json` configuration
- Check build logs in Vercel dashboard

### Import Errors
- Verify `requirements.txt` has all dependencies
- Check `api/index.py` adds project root to `sys.path`

### Environment Variables
- Verify variables set in Vercel dashboard
- Redeploy after changing variables
- Check variable names are exact (case-sensitive)

---

## 📚 Full Documentation

See [VERCEL_DEPLOYMENT_GUIDE.md](./VERCEL_DEPLOYMENT_GUIDE.md) for detailed documentation.

---

## 🆘 Need Help?

- Check Vercel build logs in dashboard
- Review [VERCEL_DEPLOYMENT_GUIDE.md](./VERCEL_DEPLOYMENT_GUIDE.md)
- Vercel Docs: [vercel.com/docs](https://vercel.com/docs)

