@echo off
REM YouTube Transcript RAG - Backend Startup Script for Windows

echo.
echo ====================================================
echo YouTube Transcript RAG - Backend Server
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

REM Change to backend directory
cd backend

REM Check if requirements are installed
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting Backend Server...
echo.
echo Server will run at: http://localhost:8000
echo Health check: http://localhost:8000/health
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
