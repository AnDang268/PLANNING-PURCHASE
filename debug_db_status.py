
from backend.database import SessionLocal, engine
from backend.models import DimVendors, DimCustomers, SystemSyncLogs
from backend.amis_accounting_client import AmisAccountingClient
from backend.models import SystemConfig
from sqlalchemy import text

def debug_status():
    db = SessionLocal()
    try:
        print("--- TABLE COUNTS ---")
        vc = db.query(DimVendors).count()
        cc = db.query(DimCustomers).count()
        logs = db.query(SystemSyncLogs).count()
        print(f"Vendors: {vc}")
        print(f"Customers: {cc}")
        print(f"SyncLogs: {logs}")
        
        print("\n--- LATEST SYNC LOGS ---")
        last_logs = db.query(SystemSyncLogs).order_by(SystemSyncLogs.start_time.desc()).limit(3).all()
        for l in last_logs:
            print(f"Log {l.log_id}: {l.action_type} - {l.status} (Processed: {l.records_processed}) Time: {l.start_time}")

        print("\n--- RAW DATA SAMPLE ---")
        # Reuse client logic to see one item
        config = db.query(SystemConfig).filter(SystemConfig.config_key == 'MISA_AMIS_ACT_APP_ID').first()
        if config:
            # Manually init client if config exists (assuming others exist too)
            app_id = config.config_value
            # For quickness, just instantiate client if we can't load all config easily
            # But getting config is safer.
            pass

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_status()
