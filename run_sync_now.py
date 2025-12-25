import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db, init_db
from backend.services.sync_service import SyncService

def run_sync():
    print(">>> Initializing DB...")
    init_db()
    
    print(">>> Starting Foreground Sync...")
    db = next(get_db())
    try:
        service = SyncService(db)
        service.sync_all_master_data()
        print(">>> Foreground Sync Completed Successfully.")
    except Exception as e:
        print(f">>> CRITICAL ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_sync()
