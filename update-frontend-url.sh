#!/bin/bash

if [ -z "$1" ]; then
    echo "❌ Please provide your Railway URL"
    echo "Usage: ./update-frontend-url.sh https://your-project.railway.app"
    exit 1
fi

RAILWAY_URL="$1"

echo "🔄 Updating frontend with Railway URL: $RAILWAY_URL"

# Update the frontend page.tsx with the actual Railway URL
sed -i.bak "s|https://your-railway-backend-url.railway.app|$RAILWAY_URL|g" frontend/src/app/page.tsx

echo "✅ Updated frontend/src/app/page.tsx"

# Rebuild the frontend
echo "🔨 Rebuilding frontend..."
cd frontend
npm run build
cd ..

echo "📦 Committing changes..."
git add .
git commit -m "Update frontend with Railway backend URL: $RAILWAY_URL"
git push origin main

echo "✅ Frontend updated and deployed!"
echo "🌐 Your app will be available at: https://mikhailsal123.github.io/TradeSphere.ai/"
echo "🔗 Backend running at: $RAILWAY_URL"
