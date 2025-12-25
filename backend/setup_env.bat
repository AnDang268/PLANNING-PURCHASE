@echo off
echo ==========================================
echo Setting up AI Demand Planning Backend
echo ==========================================

cd backend

echo 1. Creating Python Virtual Environment...
python -m venv venv

echo 2. Activating Virtual Environment...
call venv\Scripts\activate

echo 3. Upgrading pip...
python -m pip install --upgrade pip

echo 4. Installing Dependencies...
pip install -r requirements.txt

echo ==========================================
echo Setup Complete!
echo To run the server, use: run_server.bat
echo ==========================================
pause
