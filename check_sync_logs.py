import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine

def check_logs():
    print(">>> Checking Sync Logs...")
    with engine.connect() as conn:
        res = conn.execute(text("SELECT TOP 5 action_type, status, error_message, end_time FROM System_Sync_Logs ORDER BY log_id DESC")).fetchall()
        for row in res:
            print(f"{row.action_type} | {row.status} | {row.error_message}")

if __name__ == "__main__":
    check_logs()
