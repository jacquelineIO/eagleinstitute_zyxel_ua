@echo off
echo ========================================
echo Creating Zyxel Captive Portal ZIP
echo ========================================
echo.

:: Check if we're in the correct directory
if not exist "ua_agree.html" (
    echo ERROR: ua_agree.html not found!
    echo Please run this script from the ua directory
    pause
    exit /b 1
)

:: Remove old ZIP if it exists
if exist "zyxel_captive_portal.zip" (
    echo Removing old ZIP file...
    del "zyxel_captive_portal.zip"
)

:: Check if required files exist
echo Checking required files...
set "missing_files="

if not exist "ua_agree.html" set "missing_files=%missing_files% ua_agree.html"
if not exist "ua_welcome.html" set "missing_files=%missing_files% ua_welcome.html"
if not exist "script.js" set "missing_files=%missing_files% script.js"
if not exist "ua.css" set "missing_files=%missing_files% ua.css"
if not exist "css_m" set "missing_files=%missing_files% css_m/"
if not exist "images" set "missing_files=%missing_files% images/"
if not exist "images_m" set "missing_files=%missing_files% images_m/"
if not exist "js" set "missing_files=%missing_files% js/"

if not "%missing_files%"=="" (
    echo ERROR: Missing required files:%missing_files%
    pause
    exit /b 1
)

echo ✅ All required files found

:: Create the ZIP file
echo.
echo Creating ZIP file...
echo Including:
echo - HTML files (ua_agree.html, ua_welcome.html)
echo - JavaScript (script.js)
echo - CSS files (ua.css, css_m/)
echo - Images (images/, images_m/)
echo - JavaScript libraries (js/)
echo.

:: Use PowerShell to create ZIP (Windows 10/11 built-in)
powershell -command "Compress-Archive -Path 'ua_agree.html','ua_welcome.html','script.js','ua.css','css_m','images','images_m','js' -DestinationPath 'zyxel_captive_portal.zip' -Force"

if %errorlevel% neq 0 (
    echo ERROR: Failed to create ZIP file
    echo Make sure PowerShell is available and try again
    pause
    exit /b 1
)

:: Check ZIP file size
echo.
echo ========================================
echo ZIP Creation Complete!
echo ========================================

for %%I in (zyxel_captive_portal.zip) do (
    echo File: %%~nxI
    echo Size: %%~zI bytes
    set /a "size_mb=%%~zI / 1024 / 1024"
)

echo Size: %size_mb% MB
echo.

if %size_mb% gtr 5 (
    echo ⚠️  WARNING: ZIP file is larger than 5MB
    echo Zyxel may have upload size limits
    echo Consider optimizing images if upload fails
) else (
    echo ✅ ZIP file size looks good for upload
)

echo.
echo Ready to upload to Zyxel USG Flex 200:
echo 1. Access Zyxel admin interface
echo 2. Navigate to Captive Portal settings  
echo 3. Upload: zyxel_captive_portal.zip
echo 4. Configure guest network to use the portal
echo.
echo Location: %CD%\zyxel_captive_portal.zip
echo ========================================

pause