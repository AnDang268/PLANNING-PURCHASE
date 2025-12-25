from backend.database import SessionLocal
from backend.services.sync_service import SyncService
import sys

print("--- MANUAL SYNC TRIGGER ---")
db = SessionLocal()
service = SyncService(db)

try:
    print("\n[1] Syncing Products...")
    service.sync_products()
    print("[SUCCESS] Product Sync Finished.")

    print("\n[2] Syncing Vendors...")
    service.sync_vendors()
    print("[SUCCESS] Vendor Sync Finished.")

    # Skipping Orders since we have some, focusing on missing Master Data
    
except Exception as e:
    print(f"\n[ERROR] Sync Failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
