@echo off
setlocal enabledelayedexpansion
title AI Adaptive Traffic Signal - Master Controller

echo ========================================================
echo   AI ADAPTIVE TRAFFIC SIGNAL CONTROL SYSTEM
echo ========================================================
echo.

:: Ensure we run from the folder where this batch script lives
cd /d "%~dp0"

:: Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .venv\Scripts\python.exe!
    echo Please make sure you are in the project root directory.
    pause
    exit /b 1
)

:: Ensure output directory exists for telemetry logging
if not exist "data\processed" (
    mkdir "data\processed"
)

echo [1/2] Launching Vision and Adaptive Controller Pipeline...
:: Use python.exe directly from .venv to avoid PATH conflicts
start "Traffic Signal - Vision Pipeline" cmd /k "cd /d "%~dp0" && .venv\Scripts\python.exe src\main.py"

echo [2/2] Waiting 3 seconds for pipeline initialization...
timeout /t 3 /nobreak >nul

echo [3/3] Launching Streamlit Telemetry Dashboard...
start "Traffic Signal - Web Dashboard" cmd /k "cd /d "%~dp0" && .venv\Scripts\python.exe -m streamlit run dashboard\app.py"

echo.
echo ========================================================
echo  System running! 
echo  - Press 'q' inside the OpenCV window to exit vision.
echo  - Close the individual terminal windows to shut down.
echo ========================================================
pause