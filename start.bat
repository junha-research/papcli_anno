@echo off
echo ========================================
echo Annotation Tool - Starting Application
echo ========================================
echo.

REM Check if setup has been run
if not exist "backend\venv" (
    echo [ERROR] Setup not complete!
    echo Please run 'setup.bat' first.
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo [ERROR] Setup not complete!
    echo Please run 'setup.bat' first.
    pause
    exit /b 1
)

echo Starting Backend and Frontend...
echo.
echo Backend will run on: http://0.0.0.0:8000
echo Frontend will run on: http://0.0.0.0:4173
echo.
echo Press Ctrl+C to stop both servers
echo ========================================
echo.

REM Start backend in a new window
start "Annotation Tool - Backend" cmd /k "cd backend && venv\Scripts\activate && python main.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
start "Annotation Tool - Frontend" cmd /k "cd frontend && npm run preview -- --host 0.0.0.0 --port 4173"

echo.
echo ========================================
echo Application Started!
echo ========================================
echo.
echo Access the application at:
echo   Local:    http://localhost:4173
echo   Network:  http://YOUR_LOCAL_IP:4173
echo.
echo Test Accounts:
echo   annotator1 / password123
echo   annotator2 / password123
echo   annotator3 / password123
echo   annotator4 / password123
echo.
echo Backend API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Two new windows have opened for Backend and Frontend.
echo Close those windows to stop the servers.
echo.
pause
