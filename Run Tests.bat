@echo off
REM Double-click this file to run the automated checks on the
REM recommendation logic (lineup, alerts, waivers, draft rankings).

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo The app hasn't been set up yet. Please run "Start Fantasy Assistant.bat" first.
    pause
    exit /b 1
)

"venv\Scripts\python.exe" -m pytest tests\ -v

echo.
pause
