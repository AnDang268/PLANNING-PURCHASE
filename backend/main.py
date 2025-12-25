from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Demand Planning API",
    description="Backend Service for Intelligent Demand Planning System",
    version="1.0.0"
)


from backend.routers import dashboard_analytics, data_management, planning, system, vendors, planning_rolling

app.include_router(dashboard_analytics.router)
app.include_router(data_management.router)
app.include_router(planning.router)
app.include_router(system.router)
app.include_router(vendors.router)
app.include_router(planning_rolling.router)

# CORS Configuration (Allow Frontend to connect)
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MISA CRM Config (Ideally move to env vars)
MISA_APP_ID = "kttwebshop"
MISA_ACCESS_KEY = "9JfVc6h2Q0Nq1mT61o14NN4Ck+Qyt7kI6Pxt9TQcd/8="
# Using a placeholder URL, please update if different
MISA_BASE_URL = "https://crmconnect.misa.vn" 

try:
    from backend.misa_client import MisaClient
except ImportError:
    from misa_client import MisaClient

misa_client = MisaClient(MISA_APP_ID, MISA_ACCESS_KEY, MISA_BASE_URL)

@app.get("/test-misa")
def test_misa_connection():
    """
    Test connection to MISA CRM by fetching first page of products.
    """
    result = misa_client.get_products(page_size=5)
    if result:
        return {"status": "success", "data": result}
    else:
        return {"status": "error", "message": "Failed to connect to MISA API"}

@app.post("/api/sync/products")
def sync_products():
    """
    Trigger Product Sync from MISA.
    """
    # In a real scenario, this would trigger a background task
    # For now, we'll fetch the first page as a demo
    try:
        data = misa_client.get_products(page_size=100)
        # TODO: Save to DB
        return {"status": "success", "message": "Products synced successfully", "count": len(data.get("data", {}).get("data", [])) if data else 0}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/sync/orders")
def sync_orders():
    """
    Trigger Order Sync from MISA.
    """
    try:
        # Fetching last 30 days as example
        from datetime import datetime, timedelta
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        data = misa_client.get_orders(from_date=from_date, to_date=to_date, page_size=100)
        # TODO: Save to DB
        return {"status": "success", "message": "Orders synced successfully", "data_preview": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/")
def read_root():
    return {"status": "active", "service": "AI Demand Planning API", "version": "1.0.0"}

from sqlalchemy import text

@app.get("/health")
def health_check():
    from backend.database import engine
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "error": str(e)}
