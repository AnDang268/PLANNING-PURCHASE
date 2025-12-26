
import sys
import os
from sqlalchemy import text, desc

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import FactInventorySnapshots, SystemSyncLogs

def check_inventory_status():
    db = SessionLocal()
    try:
        # Check Count
        count = db.query(FactInventorySnapshots).count()
        print(f"FactInventorySnapshots Count: {count}")
        
        # Check Recent Logs
        print("\nRecent SystemSyncLogs (Last 5):")
        logs = db.query(SystemSyncLogs).order_by(desc(SystemSyncLogs.start_time)).limit(5).all()
        for log in logs:
            print(f"- [{log.start_time}] {log.source} - {log.action_type}: {log.status}")
            if log.error_message:
                print(f"   Error: {log.error_message.encode('ascii', 'replace').decode()}")
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_inventory_status()
