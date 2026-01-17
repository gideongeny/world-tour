@echo off
echo ============================================================
echo 🚀 WORLD TOUR - Automated Deployment
echo ============================================================
echo This script will:
echo 1. Build the frontend
echo 2. Deploy to Firebase
echo 3. Push to GitHub
echo ============================================================
echo.

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js 16+ and try again
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Firebase CLI is installed
firebase --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Firebase CLI not found. Installing...
    npm install -g firebase-tools
    if errorlevel 1 (
        echo ❌ Failed to install Firebase CLI
        pause
        exit /b 1
    )
)

echo.
echo 📦 Step 1: Installing frontend dependencies...
cd frontend
if not exist "node_modules" (
    call npm install
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo ✅ Dependencies already installed
)
cd ..

echo.
echo 🔨 Step 2: Building frontend...
cd frontend
call npm run build
if errorlevel 1 (
    echo ❌ Build failed
    pause
    exit /b 1
)
cd ..
echo ✅ Frontend built successfully!

echo.
echo 📤 Step 3: Pushing to GitHub...
git add .
git commit -m "Deploy: Auto-deployment %date% %time%" || echo No changes to commit
git push origin main
if errorlevel 1 (
    echo ⚠️ Warning: Failed to push to GitHub. Continuing with Firebase deployment...
) else (
    echo ✅ Pushed to GitHub successfully!
)

echo.
echo 🔥 Step 4: Deploying to Firebase...
firebase deploy --only hosting
if errorlevel 1 (
    echo ❌ Firebase deployment failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo ✅ DEPLOYMENT COMPLETE!
echo ============================================================
echo Your website is now live on Firebase!
echo Backend is running automatically on Render
echo ============================================================
echo.
pause
