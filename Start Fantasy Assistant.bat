@echo off
REM Double-click this file to start the Fantasy Football Assistant.
REM It sets everything up automatically the first time, then just runs
REM the app on every launch after that.

cd /d "%~dp0"

set PY_LAUNCHER=py
where py >nul 2>nul
if errorlevel 1 (
    set PY_LAUNCHER="%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
)

if not exist "venv\Scripts\python.exe" (
    echo Setting up the application for the first time. This may take a minute...
    %PY_LAUNCHER% -3 -m venv venv
    if errorlevel 1 (
        echo.
        echo Could not create the virtual environment. Make sure Python is installed.
        pause
        exit /b 1
    )
)

echo Checking required components...
"venv\Scripts\python.exe" -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo.
    echo Something went wrong installing required components. See the message above.
    pause
    exit /b 1
)

echo.
echo Starting the Fantasy Football Assistant dashboard...
echo A browser window will open automatically. To stop the app, close this window.
echo.

start "" http://127.0.0.1:5055/

"venv\Scripts\python.exe" run.py

pause
