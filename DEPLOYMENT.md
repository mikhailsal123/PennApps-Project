# TradeSphere.ai Deployment Guide

This guide will help you deploy your TradeSphere.ai application to GitHub Pages and a backend hosting service.

## 🚀 Frontend Deployment (GitHub Pages)

### Step 1: Prepare Repository
```bash
# Make sure you're in the project root
cd /Users/michaelsaleev/PennApps-Project

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Add your GitHub repository as remote
git remote add origin https://github.com/your-username/PennApps-Project.git
git push -u origin main
```

### Step 2: Enable GitHub Pages
1. Go to your GitHub repository
2. Click **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. The workflow will automatically deploy when you push to main

### Step 3: Update Backend URL
1. Deploy your Flask backend (see Backend Deployment section)
2. Update the backend URL in `frontend/src/app/page.tsx`:
   ```typescript
   src={process.env.NODE_ENV === 'production' 
       ? "https://your-actual-backend-url.vercel.app" 
       : "http://localhost:5002"
   }
   ```

## 🔧 Backend Deployment (Vercel)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Deploy Backend
```bash
# In the project root (not frontend folder)
vercel

# Follow the prompts:
# - Set up and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N
# - Project name: tradesphere-backend
# - Directory: ./
# - Override settings? N
```

### Step 3: Configure Environment Variables
1. Go to your Vercel dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add: `CEREBRAS_TOKEN` = `csk-42x2pme9cv39vddm69tpmec5exyv4r6ch5c8n8rdfdrcrmnh`

### Step 4: Update Frontend
Update the backend URL in your Next.js app with the Vercel URL.

## 🌐 Alternative Backend Hosting

### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Render
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`
5. Add environment variable: `CEREBRAS_TOKEN`

## 📁 Project Structure for Deployment

```
PennApps-Project/
├── frontend/                 # Next.js frontend
│   ├── src/app/
│   ├── package.json
│   └── next.config.ts
├── app.py                   # Flask backend
├── Portfolio.py
├── StockData.py
├── requirements.txt
└── .github/workflows/       # GitHub Actions
    └── deploy-nextjs.yml
```

## 🔄 Deployment Workflow

1. **Frontend**: Automatically deploys to GitHub Pages when you push to main
2. **Backend**: Deploy once to Vercel/Railway/Render
3. **Update**: Change backend URL in frontend when backend is deployed

## 🌍 Live URLs

After deployment:
- **Frontend**: `https://your-username.github.io/PennApps-Project/`
- **Backend**: `https://your-backend-url.vercel.app`

## 🐛 Troubleshooting

### Frontend Issues
- Check GitHub Actions logs in your repository
- Ensure `next.config.ts` has correct `basePath` and `assetPrefix`
- Verify all static assets are in the `out/` folder

### Backend Issues
- Check Vercel/Railway/Render logs
- Verify environment variables are set
- Ensure `requirements.txt` includes all dependencies

### CORS Issues
- Add CORS headers to your Flask app
- Update iframe `sandbox` attributes if needed

## 📝 Next Steps

1. Deploy backend to Vercel
2. Update frontend with backend URL
3. Push changes to trigger GitHub Pages deployment
4. Test the full application

Your TradeSphere.ai will be live at: `https://your-username.github.io/PennApps-Project/`
