@echo off
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo "Starting Planning & Purchase System..."
echo "Root Path: %PROJECT_ROOT%"

:: 1. Start Backend (Background)
echo "Starting Backend..."
:: Run from ROOT so 'backend' module is found
start "Planning Backend" cmd /k "python -m uvicorn backend.main:app --reload --port 8000"

:: 2. Wait for Backend
timeout /t 5

:: 3. Start Frontend (Production Mode)
echo "Starting Frontend..."
cd /d "%PROJECT_ROOT%frontend"
cmd /k "npm start"
