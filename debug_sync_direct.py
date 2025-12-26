
import sys
import os

sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.services.sync_service import SyncService

def debug_sync():
    print("Initializing SyncService...")
    db = SessionLocal()
    try:
        service = SyncService(db)
        print("Starting CRM Inventory Sync...")
        service.sync_crm_inventory()
        print("Sync Completed.")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_sync()
