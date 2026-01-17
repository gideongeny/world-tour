@echo off
echo ============================================================
echo 🚀 WORLD TOUR - Starting Development Server
echo ============================================================
echo Starting both Backend (Flask) and Frontend (Vite)...
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js 16+ and try again
    pause
    exit /b 1
)

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo 📦 Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

REM Check if root dependencies are installed (concurrently)
if not exist "node_modules" (
    echo 📦 Installing root dependencies...
    call npm install
)

echo.
echo ✅ All dependencies installed!
echo.
echo 🎯 Starting services...
echo - Backend: http://localhost:5000
echo - Frontend: http://localhost:5173
echo.
echo Press Ctrl+C to stop both services
echo ============================================================
echo.

REM Start both services using concurrently
npx concurrently --kill-others --prefix-colors "blue,green" --prefix "{name}" --names "BACKEND,FRONTEND" "python app.py" "cd frontend && npm run dev"

pause
