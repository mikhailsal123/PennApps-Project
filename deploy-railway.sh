#!/bin/bash

echo "🚀 Deploying TradeSphere.ai to Railway..."
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

echo "📋 Please follow these steps:"
echo ""
echo "1. Go to https://railway.app and sign up with GitHub"
echo "2. Click 'New Project' → 'Deploy from GitHub repo'"
echo "3. Select your repository: mikhailsal123/PennApps-Project"
echo "4. Railway will automatically detect it's a Python project"
echo "5. Wait for deployment to complete"
echo "6. Copy the generated URL (something like https://your-project.railway.app)"
echo ""
echo "🔧 After deployment, run this command to update the frontend:"
echo "   ./update-frontend-url.sh YOUR_RAILWAY_URL"
echo ""
echo "📖 For detailed instructions, see RAILWAY_DEPLOYMENT.md"
