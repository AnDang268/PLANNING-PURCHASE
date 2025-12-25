@echo off
cd /d "%~dp0"

echo [INFO] 1. Stopping Windows Services (Prevent Conflict)...
"%~dp0nssm.exe" stop PlanningBackend >nul 2>&1
"%~dp0nssm.exe" stop PlanningFrontend >nul 2>&1

echo [INFO] 2. Killing leftover processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

echo.
echo [INFO] 3. Starting App Manually (STABLE MODE)...
echo.

echo [3a] Starting Backend (Python API)...
:: Removed --reload to prevent auto-shutdown issues
start "Planning Backend (DO NOT CLOSE)" cmd /k "C:\Python314\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

echo.
echo [3b] Starting Frontend (Next.js)...
cd frontend
start "Planning Frontend (DO NOT CLOSE)" cmd /k "npm start"

echo.
echo [SUCCESS] App is launching...
echo Please KEEP the 2 Black Windows OPEN.
echo.
echo Link: http://localhost:3000/dashboard/data
echo.
pause
