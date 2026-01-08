@echo off
title P.R.I.S.M - Voice Assistant
color 0d

echo ================================================
echo    P.R.I.S.M - Voice Assistant Starting...
echo ================================================
echo.

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo [INFO] Starting P.R.I.S.M...
echo [INFO] Press Ctrl+C to stop
echo.

python Main.py

pause