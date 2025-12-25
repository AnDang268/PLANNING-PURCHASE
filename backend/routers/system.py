
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import os
from dotenv import set_key
from backend.database import get_db, reload_engine
# Use current env values
from backend.database import server, database as db_name, username

router = APIRouter(
    prefix="/api/system",
    tags=["System Health"],
)

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Perform a comprehensive health check.
    """
    start_time = time.time()
    status = "healthy"
    details = {}
    
    # Reload env vars to get latest display info (in case of manual file edit)
    # Ideally simpler, but for now we trust global imports or re-read os.getenv
    current_server = os.getenv("DB_SERVER", server)
    current_db = os.getenv("DB_DATABASE", db_name)
    
    try:
        # 1. Test Select
        db.execute(text("SELECT 1"))
        latency = (time.time() - start_time) * 1000 # ms
        
        details["database"] = {
            "status": "connected",
            "latency_ms": round(latency, 2),
            "name": current_db,
            "server": "***" + str(current_server)[-4:] if len(str(current_server)) > 4 else "localhost"
        }
    except Exception as e:
        status = "unhealthy"
        details["database"] = {
            "status": "disconnected",
            "error": str(e),
             "name": current_db,
            "server": "***" + str(current_server)[-4:] if len(str(current_server)) > 4 else "localhost"
        }
        
    return {
        "status": status,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": details
    }

@router.post("/config/database")
def update_database_config(
    db_server: str = Body(..., embed=True),
    db_name: str = Body(..., embed=True),
    username: str = Body(..., embed=True),
    password: str = Body(..., embed=True)
):
    """
    Update Database Configuration in .env and reload engine.
    """
    env_path = os.path.join(os.getcwd(), ".env")
    
    try:
        # 1. Update .env file
        set_key(env_path, "DB_SERVER", db_server)
        set_key(env_path, "DB_DATABASE", db_name)
        set_key(env_path, "DB_USER", username)
        set_key(env_path, "DB_PASSWORD", password)
        
        # 2. Reload Engine
        reload_engine()
        
        return {"status": "success", "message": "Database configuration updated and reloaded."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")
