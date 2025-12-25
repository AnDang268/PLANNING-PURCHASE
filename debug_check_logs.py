from backend.database import SessionLocal
from backend.models import SystemSyncLogs
from sqlalchemy import desc

print("--- RECENT SYNC LOGS ---")
db = SessionLocal()
try:
    logs = db.query(SystemSyncLogs).order_by(desc(SystemSyncLogs.id)).limit(5).all()
    for log in logs:
        print(f"[{log.id}] {log.action_type} | {log.status}")
        print(f"   Time: {log.start_time} -> {log.end_time}")
        print(f"   Processed: {log.records_processed}")
        if log.error_message:
            print(f"   ERROR: {log.error_message}")
        print("-" * 30)
except Exception as e:
    print(f"Failed to read logs: {e}")
finally:
    db.close()
