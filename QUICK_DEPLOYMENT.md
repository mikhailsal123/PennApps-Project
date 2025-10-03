# Quick Deployment Guide

## Option 1: Railway (Recommended)

1. **Go to [railway.app](https://railway.app)** and sign up with GitHub
2. **Click "New Project"** → **"Deploy from GitHub repo"**
3. **Select your repository**: `mikhailsal123/PennApps-Project`
4. **Railway will auto-detect** it's a Python project
5. **Wait for deployment** (2-3 minutes)
6. **Copy the URL** (e.g., `https://tradesphere-production.railway.app`)
7. **Run**: `./update-frontend-url.sh YOUR_RAILWAY_URL`

## Option 2: Render.com (Alternative)

1. **Go to [render.com](https://render.com)** and sign up with GitHub
2. **Click "New"** → **"Web Service"**
3. **Connect repository**: `mikhailsal123/PennApps-Project`
4. **Configure**:
   - Name: `tradesphere-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python3 app.py`
   - Environment Variable: `FLASK_ENV=production`
5. **Click "Create Web Service"**
6. **Wait for deployment** (3-5 minutes)
7. **Copy the URL** (e.g., `https://tradesphere-backend.onrender.com`)
8. **Run**: `./update-frontend-url.sh YOUR_RENDER_URL`

## After Backend Deployment

Your frontend is already deployed at:
**https://mikhailsal123.github.io/TradeSphere.ai/**

Once you update the backend URL, the iframe will load your Flask application.

## Test Your Deployment

1. **Backend**: Visit your Railway/Render URL directly
2. **Frontend**: Visit https://mikhailsal123.github.io/TradeSphere.ai/
3. **Full App**: Click "Execute Trades" in the frontend

## Troubleshooting

- **Backend not loading**: Check Railway/Render logs
- **Frontend not loading backend**: Verify the URL in `frontend/src/app/page.tsx`
- **CORS errors**: Railway/Render handle CORS automatically

## Files Ready for Deployment

✅ `railway.json` - Railway configuration  
✅ `render.yaml` - Render configuration  
✅ `Procfile` - Process definition  
✅ `requirements.txt` - Python dependencies  
✅ `app.py` - Updated for production  
✅ `frontend/` - Ready for GitHub Pages  

## Quick Commands

```bash
# Deploy to Railway
./deploy-railway.sh

# Deploy to Render
./deploy-render.sh

# Update frontend with backend URL
./update-frontend-url.sh https://your-backend-url.com
```
