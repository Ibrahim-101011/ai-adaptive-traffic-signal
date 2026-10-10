@echo off
setlocal enabledelayedexpansion
title AI Adaptive Traffic Signal - Launcher
color 0A

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment .venv not found!
    pause
    exit /b 1
)

if not exist "data\processed" (
    mkdir "data\processed"
)

echo [1/2] Launching Digital Twin Simulation...
start "Traffic Simulation" cmd /k "call .venv\Scripts\activate.bat && python -u src\main.py"

timeout /t 3 /nobreak >nul

echo [2/2] Launching Streamlit Telemetry Dashboard...
start "Telemetry Dashboard" cmd /k "call .venv\Scripts\activate.bat && streamlit run dashboard\app.py"

echo System running!
pause