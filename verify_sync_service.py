from backend.database import SessionLocal
from backend.services.sync_service import SyncService
import sys

# Setup DB Session
db = SessionLocal()

print("--- VERIFYING SYNC SERVICE ---")
try:
    service = SyncService(db)
    
    # 1. Test Units Sync (Usually small and fast)
    print("\n[TEST] Syncing UNITS...")
    service.sync_units()
    
    # 2. Test Product Groups Sync (To verify hierarchy logic)
    print("\n[TEST] Syncing PRODUCT GROUPS...")
    service.sync_product_groups()
    
    # 3. Test Products Sync (Limit batch size in service, so it should be fine)
    print("\n[TEST] Syncing PRODUCTS...")
    service.sync_products()

    print("\n[SUCCESS] Sync verification script finished.")

except Exception as e:
    print(f"\n[ERROR] Sync verification failed: {e}")
finally:
    db.close()
