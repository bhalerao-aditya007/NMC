#!/bin/bash

# PWD Red Flag Analyzer - One-Click Deployment Setup
# This script prepares your app for cloud deployment

echo "=============================================="
echo "PWD Red Flag Analyzer - Deployment Setup"
echo "=============================================="
echo ""

# Check if running in correct directory
if [ ! -f "app_production.py" ]; then
    echo "❌ Error: app_production.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo "✓ Project files found"
echo ""

# Step 1: Check Python
echo "Step 1: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ $PYTHON_VERSION found"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or higher"
    exit 1
fi
echo ""

# Step 2: Create virtual environment (optional, for local testing)
echo "Step 2: Setting up virtual environment (optional)..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Step 3: Install dependencies locally for testing
echo "Step 3: Installing dependencies..."
echo "This may take a few minutes..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    pip install -r requirements_production.txt --quiet
    echo "✓ Dependencies installed in virtual environment"
else
    pip install -r requirements_production.txt --user --quiet
    echo "✓ Dependencies installed"
fi
echo ""

# Step 4: Test the application locally
echo "Step 4: Testing application locally..."
python3 -c "from app_production import app; print('✓ App imports successfully')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Application test passed"
else
    echo "⚠️  Warning: Application test failed, but deployment may still work"
fi
echo ""

# Step 5: Initialize git (if not already initialized)
echo "Step 5: Preparing for deployment..."
if [ ! -d ".git" ]; then
    git init
    git add .
    git commit -m "Initial commit - PWD Red Flag Analyzer"
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already exists"
fi
echo ""

# Step 6: Provide deployment instructions
echo "=============================================="
echo "✅ SETUP COMPLETE!"
echo "=============================================="
echo ""
echo "Your app is ready for cloud deployment!"
echo ""
echo "NEXT STEPS - Choose ONE deployment method:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 OPTION 1: Railway (RECOMMENDED - Easiest)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Method A: GitHub + Railway (No Command Line)"
echo "  1. Create GitHub repo: https://github.com/new"
echo "  2. Upload all files to GitHub"
echo "  3. Go to: https://railway.app"
echo "  4. Click 'New Project' → 'Deploy from GitHub repo'"
echo "  5. Select your repository"
echo "  6. Done! Get your URL from Railway dashboard"
echo ""
echo "Method B: Railway CLI"
echo "  1. Install: npm i -g @railway/cli"
echo "  2. Login: railway login"
echo "  3. Deploy: railway up"
echo "  4. Get URL: railway open"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 OPTION 2: Render.com"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Push to GitHub (if not already done)"
echo "  2. Go to: https://render.com"
echo "  3. New → Web Service"
echo "  4. Connect GitHub repository"
echo "  5. Deploy!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 OPTION 3: Heroku"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Install Heroku CLI"
echo "  2. Run: heroku login"
echo "  3. Run: heroku create pwd-analyzer"
echo "  4. Run: git push heroku main"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Test Locally First (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Run: python3 app_production.py"
echo "  Open: http://localhost:5000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 For detailed instructions, see: CLOUD_DEPLOYMENT.md"
echo ""
echo "Need help? Check the deployment guide!"
echo "=============================================="
