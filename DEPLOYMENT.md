# Deployment Guide to Production (Windows)

This document guides you through deploying the **Planning & Purchase System** to a Production environment (Windows Server or dedicated PC).

## 1. Prerequisites
Ensure the server has the following installed:
*   **Python 3.11+**: [Download](https://www.python.org/downloads/)
    *   *Check: `python --version`*
*   **Node.js 20+ (LTS)**: [Download](https://nodejs.org/)
    *   *Check: `node -v`*
*   **SQL Server**: Ensure your database server is running and accessible (Local or Remote).
*   **Git**: [Download](https://git-scm.com/) (Optional, for pulling code).

## 2. Environment Configuration
On the Production Server, create a `.env` file in the root directory (Project Folder):

```ini
DB_SERVER=LOCALHOST\SQLEXPRESS
DB_NAME=PlanningPurchaseDB
DB_USER=
DB_PASSWORD=
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUSTED_CONNECTION=yes

# Production Tuning
BACKEND_PORT=8000
FRONTEND_PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 3. Deployment Steps

### Step A: Backend (Python API)
1.  Open Command Prompt (Admin).
2.  Navigate to Project Root.
3.  Install Dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run Database Migrations (Initialize Tables):
    ```bash
    python -m backend.migrate_profiles
    python -m backend.migrations.init_db 
    ```

### Step B: Frontend (Next.js Web App)
1.  Navigate to `frontend` folder:
    ```bash
    cd frontend
    ```
2.  Install Dependencies:
    ```bash
    npm install
    ```
3.  **Build for Production** (Crucial Step):
    ```bash
    npm run build
    ```
    *This creates an optimized `.next` folder.*

## 4. Running as a Service (Auto-Start)
To ensure the app runs automatically when the server restarts, use **NSSM** (Non-Sucking Service Manager).

### Install NSSM
1.  Download NSSM: [https://nssm.cc/download](https://nssm.cc/download)
2.  Extract `nssm.exe` to `C:\Windows\System32`.

### Create Backend Service
Run CMD as Admin:
```bash
nssm install PlanningBackend "python" "-m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
nssm set PlanningBackend AppDirectory "D:\path\to\project"
nssm start PlanningBackend
```

### Create Frontend Service
Run CMD as Admin:
```bash
nssm install PlanningFrontend "npm" "start"
nssm set PlanningFrontend AppDirectory "D:\path\to\project\frontend"
nssm start PlanningFrontend
```

## 5. Maintenance
*   **Backup**: Schedule daily backups of SQL Server DB.
*   **Logs**: Check generic logs via Event Viewer (if using NSSM) or configure Uvicorn logging.
