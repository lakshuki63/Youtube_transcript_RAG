@echo off
REM YouTube Transcript RAG - Setup Script for Windows

echo.
echo ====================================================
echo YouTube Transcript RAG - Extension Setup
echo ====================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org
    pause
    exit /b 1
)

echo Step 1: Generating extension icons...
python setup.py
if errorlevel 1 (
    echo WARNING: Could not generate icons automatically
    echo You can manually create or skip this step
)

echo.
echo Step 2: Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo.
echo ====================================================
echo Setup Complete!
echo ====================================================
echo.
echo Next steps:
echo 1. Run start_backend.bat to start the server
echo 2. Open chrome://extensions/ in Chrome
echo 3. Enable Developer mode (top right)
echo 4. Click "Load unpacked"
echo 5. Select the "chrome_extension" folder
echo 6. Go to a YouTube video and configure your API token
echo.
echo For more info, read SETUP_GUIDE.md
echo.

pause
