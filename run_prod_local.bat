@echo off
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo "==================================================="
echo "   PLANNING & PURCHASING SYSTEM - LOCAL PROD       "
echo "==================================================="
echo "Root Path: %PROJECT_ROOT%"

:: 1. Backend (Uvicorn Production)
echo.
echo "[1/3] Starting Backend (Uvicorn Production Mode)..."
:: Using --workers 2 for stability, --access-log for debugging
start "Backend API (Prod)" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2"

:: 2. Frontend Build (If missing or forced)
if exist "%PROJECT_ROOT%frontend\.next" (
    echo.
    echo "[2/3] Frontend build found. Skipping build..."
    echo "      (Run 'npm run build' manually if you changed code)"
) else (
    echo.
    echo "[2/3] Building Frontend..."
    cd /d "%PROJECT_ROOT%frontend"
    call npm run build
    cd /d "%PROJECT_ROOT%"
)

:: 3. Frontend Start
echo.
echo "[3/3] Starting Frontend (Next.js Production)..."
cd /d "%PROJECT_ROOT%frontend"
start "Frontend UI (Prod)" cmd /k "npm start"

echo.
echo "==================================================="
echo " SYSTEM RUNNING "
echo " Backend: http://localhost:8000/docs"
echo " Frontend: http://localhost:3000"
echo "==================================================="
timeout /t 5
