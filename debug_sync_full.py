
import sys
import logging
from backend.database import SessionLocal
from backend.services.sync_service import SyncService

# Configure logging to file and stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sync_debug.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_debug_sync():
    print("Initialize DB Session...")
    db = SessionLocal()
    try:
        service = SyncService(db)
        print("Starting Sync for Customers & Vendors...")
        
        # Manually trigger the specific sync method
        service.sync_customers_and_vendors()
        
        print("Sync Function Returned.")
        
        # Verify INSIDE session
        from backend.models import DimCustomers
        count = db.query(DimCustomers).count()
        print(f"Count inside session: {count}")
        
    except Exception as e:
        print(f"Sync Crashed: {e}")
        logging.exception("Crash")
    finally:
        db.close()
        print("Session Closed.")

if __name__ == "__main__":
    run_debug_sync()
