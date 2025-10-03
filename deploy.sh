#!/bin/bash

echo "🚀 TradeSphere.ai Deployment Script"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📋 Deployment Options:"
echo "1. Deploy Frontend to GitHub Pages"
echo "2. Deploy Backend to Vercel"
echo "3. Deploy Both"
echo "4. Exit"
echo ""

read -p "Choose an option (1-4): " choice

case $choice in
    1)
        echo "🌐 Deploying Frontend to GitHub Pages..."
        cd frontend
        npm install
        npm run build
        echo "✅ Frontend built successfully!"
        echo "📝 Next steps:"
        echo "   1. Commit and push your changes"
        echo "   2. GitHub Actions will automatically deploy to Pages"
        echo "   3. Your site will be at: https://your-username.github.io/PennApps-Project/"
        ;;
    2)
        echo "🔧 Deploying Backend to Vercel..."
        if ! command -v vercel &> /dev/null; then
            echo "📦 Installing Vercel CLI..."
            npm install -g vercel
        fi
        vercel
        echo "✅ Backend deployed to Vercel!"
        echo "📝 Next steps:"
        echo "   1. Copy the Vercel URL"
        echo "   2. Update frontend/src/app/page.tsx with the URL"
        echo "   3. Redeploy frontend"
        ;;
    3)
        echo "🚀 Deploying Both Frontend and Backend..."
        
        # Deploy backend first
        echo "🔧 Deploying Backend to Vercel..."
        if ! command -v vercel &> /dev/null; then
            echo "📦 Installing Vercel CLI..."
            npm install -g vercel
        fi
        vercel
        
        echo "✅ Backend deployed! Please copy the Vercel URL."
        read -p "Enter your Vercel backend URL: " backend_url
        
        # Update frontend with backend URL
        echo "🔄 Updating frontend with backend URL..."
        sed -i.bak "s|https://your-backend-url.vercel.app|$backend_url|g" frontend/src/app/page.tsx
        
        # Deploy frontend
        echo "🌐 Building frontend..."
        cd frontend
        npm install
        npm run build
        
        echo "✅ Both deployments complete!"
        echo "📝 Final steps:"
        echo "   1. Commit and push your changes"
        echo "   2. GitHub Actions will deploy frontend to Pages"
        echo "   3. Your site will be at: https://your-username.github.io/PennApps-Project/"
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option. Please choose 1-4."
        exit 1
        ;;
esac
