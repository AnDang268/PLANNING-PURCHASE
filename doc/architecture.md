# System Architecture

## 1. High-Level Architecture

The system follows a **Microservices-oriented** architecture with three main components:

1.  **Frontend (Web Application)**: Next.js + React
2.  **Backend (AI Service)**: Python FastAPI
3.  **Database**: SQL Server

```mermaid
graph TD
    A[User (Browser)] -->|HTTP/REST| B[Frontend (Next.js)]
    B -->|API Calls| C[Backend (FastAPI)]
    C -->|SQL/ODBC| D[(SQL Server)]
    C -->|REST API| E[MISA AMIS CRM]
    C -->|Internal Logic| F[AI Engine (StatsForecast/XGBoost)]
```

## 2. Component Details

### 2.1 Frontend
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **UI Library**: Shadcn/UI + TailwindCSS
- **State Management**: React Query (Server state), Context API (Local state)
- **Role**: Displays dashboards, planning grids, and manages user interactions.

### 2.2 Backend
- **Framework**: FastAPI
- **Language**: Python 3.10+
- **Data Access**: SQLAlchemy + PyODBC
- **AI/ML**: `statsforecast` (Time-series), `scikit-learn` (Regression)
- **Role**:
    - **Data Ingestion**: Syncs data from MISA AMIS.
    - **Data Processing**: Cleans and transforms raw data into fact tables.
    - **Forecasting**: Runs AI models to predict demand.
    - **API Provider**: Serves data to the Frontend.

### 2.3 Database
- **System**: Microsoft SQL Server 2019/2022
- **Schema Design**: Star Schema (Data Warehousing style)
    - **Dimensions (`Dim_*`)**: Products, Customers, Vendors, Warehouses.
    - **Facts (`Fact_*`)**: Sales, Inventory Snapshots, Forecasts, Purchase Plans.
    - **System (`System_*`)**: Configs, Sync Logs.

## 3. Data Flow

1.  **Ingestion**: Backend Cronjob/Trigger calls MISA API -> Raw JSON -> Transformed to SQL Tables (`Dim_Products`, `Fact_Sales`).
2.  **Snapshotting**: Daily job captures `Fact_Inventory_Snapshots` from MISA (current stock).
3.  **Analysis**:
    - AI Engine reads `Fact_Sales`.
    - Generates predictions -> `Fact_Forecasts`.
    - Calculates `Fact_Purchase_Plans` based on Forecast + Inventory + Lead Time.
4.  **Presentation**: Frontend queries `Fact_Purchase_Plans` via Backend API for user review.
