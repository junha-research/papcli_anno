@echo off
echo ========================================
echo Annotation Tool - Initial Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.9 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [1/4] Setting up Backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
echo Installing Python dependencies...
call venv\Scripts\activate
pip install -r requirements.txt

REM Initialize database
echo Initializing database...
python init_db.py

cd ..

echo.
echo [2/4] Setting up Frontend...
cd frontend

REM Install Node dependencies
echo Installing Node.js dependencies...
call npm install

REM Build frontend
echo Building frontend...
call npm run build

cd ..

echo.
echo [3/4] Creating .env file...
REM Get public IP (optional)
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set LOCAL_IP=%%a
set LOCAL_IP=%LOCAL_IP: =%

REM Create .env file
echo VITE_API_URL=http://localhost:8000/api > frontend\.env
echo Created frontend\.env with default localhost configuration

echo.
echo [4/4] Setup Complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Run 'start.bat' to start the application
echo 2. Access the app at http://localhost:4173
echo.
echo For external access:
echo 1. Update frontend\.env with your public IP
echo 2. Configure port forwarding (8000, 4173)
echo 3. Open Windows Firewall for ports 8000 and 4173
echo ========================================
echo.
pause
