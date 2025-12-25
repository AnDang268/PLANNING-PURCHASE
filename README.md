# Intelligent Demand Planning System

## 1. Prerequisites
*   Node.js 18+
*   Python 3.10+
*   SQL Server 2019/2022 Developer Edition

## 2. Setup Database
1.  Open **SQL Server Management Studio (SSMS)**.
2.  Create a new database named `PlanningPurchaseDB`.
3.  Run the script `database/schema.sql` to create tables.

## 3. Setup Backend (AI Service)
1.  Navigate to `backend` folder.
2.  Run `setup_env.bat` to install Python dependencies.
3.  Run `../run_backend.bat` to start the API Server.
    *   API Docs: http://localhost:8000/docs

## 4. Setup Frontend (Web App)
1.  Navigate to `frontend` folder.
2.  Run `npm install` (if not already done).
3.  Run `npm run dev` to start the Web App.
    *   URL: http://localhost:3000

## 5. Project Structure
*   `frontend/`: Next.js Web Application.
*   `backend/`: Python FastAPI Service (AI Engine).
*   `database/`: SQL Scripts.
