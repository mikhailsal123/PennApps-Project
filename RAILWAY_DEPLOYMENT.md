# Railway Deployment Guide

This guide will help you deploy your Flask backend to Railway.

## Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Connect your GitHub repository

## Step 2: Deploy to Railway

1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository: `mikhailsal123/TradeSphere.ai`
4. Railway will automatically detect it's a Python project

## Step 3: Configure Environment Variables

In Railway dashboard, go to your project → Variables tab and add:

```
FLASK_ENV=production
PORT=5000
```

## Step 4: Update Frontend URL

Once deployed, Railway will give you a URL like:
```
https://your-project-name.railway.app
```

Update the iframe URL in `frontend/src/app/page.tsx`:
```typescript
src={process.env.NODE_ENV === 'production' 
    ? "https://your-project-name.railway.app" 
    : "http://localhost:5002"
}
```

## Step 5: Redeploy Frontend

After updating the backend URL, rebuild and redeploy your frontend:

```bash
cd frontend
npm run build
git add .
git commit -m "Update backend URL for Railway deployment"
git push origin main
```

## Step 6: Test the Full Application

1. Your frontend will be at: `https://mikhailsal123.github.io/TradeSphere.ai/`
2. Your backend will be at: `https://your-project-name.railway.app`
3. The iframe in your frontend should now load the Flask application

## Troubleshooting

### Backend not responding:
- Check Railway logs in the dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify environment variables are set

### CORS issues:
- Add CORS headers to your Flask app if needed
- Railway handles most CORS automatically

### Frontend not loading backend:
- Check the iframe URL is correct
- Verify the backend is running and accessible
- Check browser console for errors

## Alternative Hosting Options

If Railway doesn't work, you can also try:

1. **Render** (render.com) - Free tier available
2. **Heroku** - Has a free tier (with limitations)
3. **PythonAnywhere** - Good for Python apps
4. **Vercel** - Can host Python with serverless functions

## Files Added for Railway

- `railway.json` - Railway configuration
- `Procfile` - Process definition
- Updated `app.py` - Environment variable support
