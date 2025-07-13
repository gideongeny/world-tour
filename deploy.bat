@echo off
echo ============================================================
echo 🚀 WORLD TOUR - RAILWAY DEPLOYMENT
echo ============================================================
echo Your app will be deployed for FREE!
echo ============================================================
echo.

echo 📋 STEP 1: Create GitHub Repository
echo ----------------------------------------
echo 1. Go to https://github.com
echo 2. Click 'New repository'
echo 3. Name it: world-tour-app
echo 4. Make it PUBLIC
echo 5. Don't initialize with README
echo 6. Click 'Create repository'
echo.

pause

echo 📋 STEP 2: Push Code to GitHub
echo ----------------------------------------
echo Please enter your GitHub repository URL:
echo (e.g., https://github.com/username/world-tour-app)
set /p repo_url="Repository URL: "

git remote add origin %repo_url%
git branch -M main
git push -u origin main

echo.
echo ✅ Code pushed to GitHub!
echo.

echo 📋 STEP 3: Deploy to Railway
echo ----------------------------------------
echo 1. Go to https://railway.app
echo 2. Click 'Sign Up' (use GitHub)
echo 3. Click 'New Project'
echo 4. Select 'Deploy from GitHub repo'
echo 5. Choose your 'world-tour-app' repository
echo 6. Click 'Deploy'
echo.

pause

echo 📋 STEP 4: Add Database
echo ----------------------------------------
echo 1. In Railway dashboard, click 'New'
echo 2. Select 'Database' → 'PostgreSQL'
echo 3. Railway will automatically set DATABASE_URL
echo.

pause

echo 📋 STEP 5: Set Environment Variables
echo ----------------------------------------
echo In Railway dashboard, go to 'Variables' and add:
echo SECRET_KEY=your-super-secret-key-here-12345
echo FLASK_ENV=production
echo.

pause

echo 📋 STEP 6: Final Setup
echo ----------------------------------------
echo 1. Wait for deployment to complete (2-3 minutes)
echo 2. Click on your app URL in Railway
echo 3. Register a new account
echo 4. Test all features
echo.

echo 🎉 YOUR APP IS LIVE!
echo ============================================================
echo ✅ Free hosting on Railway
echo ✅ PostgreSQL database included
echo ✅ SSL certificate automatic
echo ✅ Custom domain available
echo ✅ Mobile app (PWA) ready
echo ============================================================
echo.

echo 🌐 Opening Railway...
start https://railway.app

pause 