@echo off
echo Starting AI Demand Planning API...
cd backend
call venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
