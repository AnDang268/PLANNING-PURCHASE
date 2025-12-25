from backend.database import SessionLocal
from backend.services.sync_service import SyncService
import traceback

print("--- STARTING MASTER SYNC ---")
try:
    db = SessionLocal()
    service = SyncService(db)
    service.sync_all_master_data()
    print("\n[DONE] Sync Finished Successfully.")
except Exception as e:
    print(f"\n[FATAL ERROR] {e}")
    traceback.print_exc()
finally:
    db.close()
