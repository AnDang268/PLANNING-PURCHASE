@echo off
echo Starting KTT Planning Purchase App...

:: Start Backend
start "KTT Backend" /D "%~dp0" cmd /k "uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

:: Start Frontend
start "KTT Frontend" /D "%~dp0frontend" cmd /k "npm run dev"

echo Application starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
pause
