@echo off
title Prism Voice Assistant
color 0d

echo ================================================
echo    Prism Voice Assistant Starting...
echo ================================================
echo.

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo [INFO] Starting Prism...
echo [INFO] Press Ctrl+C to stop or say "bye"
echo.

python Main.py

echo.
echo [INFO] Prism has been shut down.
timeout /t 3 /nobreak >nul