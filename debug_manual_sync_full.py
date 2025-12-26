from backend.database import SessionLocal
from backend.services.sync_service import SyncService
import sys
import io

# Force UTF-8 encoding for stdout/stderr to avoid charmap errors on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def run_sync():
    db = SessionLocal()
    try:
        service = SyncService(db)
        print("Starting Sync for PARTNERS (and Groups)...")
        service.sync_customers_and_vendors()
        print("Sync Completed.")
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_sync()
