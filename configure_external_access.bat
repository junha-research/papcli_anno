@echo off
echo ========================================
echo Configure External Access
echo ========================================
echo.

set /p PUBLIC_IP="Enter your public IP address (or press Enter to skip): "

if "%PUBLIC_IP%"=="" (
    echo Skipping external access configuration.
    echo Using localhost configuration.
    echo VITE_API_URL=http://localhost:8000/api > frontend\.env
) else (
    echo Configuring for external access...
    echo VITE_API_URL=http://%PUBLIC_IP%:8000/api > frontend\.env
    echo.
    echo ========================================
    echo Configuration Complete!
    echo ========================================
    echo.
    echo Frontend will use: http://%PUBLIC_IP%:8000/api
    echo.
    echo Next Steps:
    echo 1. Configure port forwarding on your router:
    echo    - Port 8000 (Backend)
    echo    - Port 4173 (Frontend)
    echo.
    echo 2. Open Windows Firewall:
    echo    Run these commands in PowerShell (as Administrator):
    echo.
    echo    netsh advfirewall firewall add rule name="Annotation Backend" dir=in action=allow protocol=TCP localport=8000
    echo    netsh advfirewall firewall add rule name="Annotation Frontend" dir=in action=allow protocol=TCP localport=4173
    echo.
    echo 3. Rebuild frontend:
    echo    cd frontend
    echo    npm run build
    echo.
    echo 4. Users can access at: http://%PUBLIC_IP%:4173
    echo ========================================
)

echo.
pause
