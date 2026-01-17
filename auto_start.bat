@echo off
REM Auto-start script - Runs in background
REM This script starts both backend and frontend automatically

echo Starting World Tour services in background...

REM Start backend in a new minimized window
start "World Tour Backend" /min python app.py

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in a new minimized window
start "World Tour Frontend" /min cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Services started in background!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo You can now enjoy the website!
echo Press any key to exit this window (services will keep running)...
pause >nul
