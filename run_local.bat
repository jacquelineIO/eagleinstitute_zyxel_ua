@echo off
echo ========================================
echo Captive Portal Local Development
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed
    pause
    exit /b 1
)

:: Create local export directory
if not exist "export" (
    echo Creating local export directory...
    mkdir export
)

:: Start both servers
echo Starting development servers...
echo.
echo This will run:
echo - API Server on http://localhost:8080
echo - HTML Server on http://localhost:8000
echo.
echo Your browser will open to the portal page.
echo Press Ctrl+C to stop all servers.
echo ========================================
echo.

python run_local.py

pause