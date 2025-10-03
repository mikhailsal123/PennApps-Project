#!/bin/bash

# TradeSphere.ai - GitHub Pages Deployment Script

echo "🚀 Setting up TradeSphere.ai for GitHub Pages..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Please run 'git init' first."
    exit 1
fi

# Create .nojekyll file to bypass Jekyll processing
echo "📝 Creating .nojekyll file..."
touch .nojekyll

# Copy static files to root for GitHub Pages
echo "📁 Copying static files..."
cp -r static ./
cp -r templates ./

# Create a simple package.json for GitHub Pages
echo "📦 Creating package.json..."
cat > package.json << EOF
{
  "name": "tradesphere-ai",
  "version": "1.0.0",
  "description": "AI-powered portfolio simulation platform",
  "main": "index.html",
  "scripts": {
    "start": "python -m http.server 8000",
    "build": "echo 'Static site ready for GitHub Pages'"
  },
  "keywords": ["portfolio", "trading", "simulation", "ai"],
  "author": "Your Name",
  "license": "MIT"
}
EOF

# Create a simple _config.yml for GitHub Pages
echo "⚙️ Creating _config.yml..."
cat > _config.yml << EOF
title: TradeSphere.ai
description: AI-powered portfolio simulation platform
baseurl: "/PennApps-Project"
url: "https://your-username.github.io"

# GitHub Pages settings
plugins:
  - jekyll-feed
  - jekyll-sitemap

# Exclude files from processing
exclude:
  - README.md
  - requirements.txt
  - app.py
  - Portfolio.py
  - StockData.py
  - main.py
  - deploy-to-github-pages.sh
  - .github/
EOF

echo "✅ GitHub Pages setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update the URL in _config.yml with your GitHub username"
echo "2. Update the README.md with your GitHub Pages URL"
echo "3. Commit and push your changes:"
echo "   git add ."
echo "   git commit -m 'Setup for GitHub Pages'"
echo "   git push origin main"
echo ""
echo "4. Enable GitHub Pages in your repository settings:"
echo "   - Go to Settings > Pages"
echo "   - Source: Deploy from a branch"
echo "   - Branch: main"
echo "   - Folder: / (root)"
echo ""
echo "🌐 Your site will be available at:"
echo "   https://your-username.github.io/PennApps-Project/"
echo ""
echo "⚠️  Note: The backend API won't work on GitHub Pages."
echo "   Consider hosting the backend on Vercel, Railway, or Render."
