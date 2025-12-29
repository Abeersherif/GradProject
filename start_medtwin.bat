@echo off
echo ========================================
echo Starting MedTwin Streamlit Server
echo ========================================
echo.

REM Kill any existing streamlit processes
echo Stopping any existing Streamlit servers...
taskkill /F /IM streamlit.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting Streamlit on port 8501...
echo.
echo Access your app at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start Streamlit
streamlit run app.py --server.port 8501

pause
