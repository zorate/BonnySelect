@echo off
REM Bonny Selects Icon Generator - Windows Batch Script
REM This script finds your logo and generates all PWA icons

echo.
echo =====================================
echo   Bonny Selects Icon Generator
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Pillow is installed
python -c "from PIL import Image" >nul 2>&1
if errorlevel 1 (
    echo Installing Pillow...
    python -m pip install Pillow
    if errorlevel 1 (
        echo Error: Could not install Pillow
        pause
        exit /b 1
    )
)

REM Look for logo files in common locations
set "LOGO_PATH="

REM Check current directory
if exist "ChatGPT_Image_Feb_21__2026__12_15_12_AM.png" (
    set "LOGO_PATH=ChatGPT_Image_Feb_21__2026__12_15_12_AM.png"
    goto found
)

REM Check Downloads folder
if exist "%USERPROFILE%\Downloads\ChatGPT_Image_Feb_21__2026__12_15_12_AM.png" (
    set "LOGO_PATH=%USERPROFILE%\Downloads\ChatGPT_Image_Feb_21__2026__12_15_12_AM.png"
    goto found
)

REM Check Desktop
if exist "%USERPROFILE%\Desktop\ChatGPT_Image_Feb_21__2026__12_15_12_AM.png" (
    set "LOGO_PATH=%USERPROFILE%\Desktop\ChatGPT_Image_Feb_21__2026__12_15_12_AM.png"
    goto found
)

REM If not found in common locations, ask user
echo Logo file not found in common locations.
echo.
echo Please provide the full path to your logo:
set /p LOGO_PATH="Logo path: "

if not exist "%LOGO_PATH%" (
    echo Error: File not found at "%LOGO_PATH%"
    pause
    exit /b 1
)

:found
echo.
echo Found logo: %LOGO_PATH%
echo.
echo Generating icons...
echo.

REM Run the Python script
python generate_icons.py "%LOGO_PATH%"

if errorlevel 1 (
    echo.
    echo Error: Icon generation failed
    pause
    exit /b 1
)

echo.
echo =====================================
echo   Success!
echo =====================================
echo.
echo Next steps:
echo 1. Update your app/__init__.py with init_updated.py
echo 2. Make sure manifest.json is in app/static/
echo 3. Make sure sw.js is in app/static/
echo 4. Restart Flask: python -m flask run
echo.
pause