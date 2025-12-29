@echo off
echo ========================================
echo   MedTwin Backend Starter
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo.

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and add your DEEPSEEK_API_KEY
    echo.
    pause
    exit /b 1
)

REM Install/update dependencies
echo Checking dependencies...
pip install -q -r requirements.txt
echo.

REM Start Flask server
echo Starting MedTwin Backend...
echo Server will run on: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py

pause
