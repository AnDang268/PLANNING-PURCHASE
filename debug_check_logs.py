
import sys
import os
from sqlalchemy import text, desc

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import SystemSyncLogs, SystemConfig

def check():
    db = SessionLocal()
    try:
        print("Checking System Config...")
        keys = ['MISA_CRM_CLIENT_ID', 'MISA_CRM_CLIENT_SECRET', 'MISA_CRM_COMPANY_CODE']
        for k in keys:
            val = db.query(SystemConfig).filter(SystemConfig.config_key == k).first()
            if val:
                v = val.config_value
                if 'SECRET' in k and v:
                    v = v[:5] + "..."
                print(f"{k}: {v}")
            else:
                print(f"{k}: <MISSING>")

        print("\nChecking LATEST System Sync Log...")
        log = db.query(SystemSyncLogs).order_by(desc(SystemSyncLogs.start_time)).first()
        if log:
            print(f"ID: {log.log_id}")
            print(f"Status: {log.status}")
            print(f"Message: {log.error_message}")
        else:
            print("No logs found.")
            
    except Exception as e:
        print(f"Error checking: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check()
