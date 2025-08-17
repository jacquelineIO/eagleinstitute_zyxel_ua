@echo off
echo ========================================
echo Captive Portal Server for Zyxel USG
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.x from https://www.python.org/
    pause
    exit /b 1
)

:: Create export directory if it doesn't exist
if not exist "C:\export" (
    echo Creating export directory at C:\export
    mkdir "C:\export"
)

:: Start the server
echo Starting Captive Portal Server on port 8080...
echo CSV files will be saved to: C:\export\export.csv
echo.
echo Press Ctrl+C to stop the server
echo ========================================
python captive_portal_server.py 8080

pause