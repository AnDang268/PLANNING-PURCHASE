from backend.database import SessionLocal
from backend.services.sync_service import SyncService
import json

def debug_sync():
    db = SessionLocal()
    try:
        service = SyncService(db)
        print(f"Service Init. AppID: {service.app_id}")
        
        # Test Connection and Token
        print("Fetching Token...")
        token = service.client.get_token()
        if not token:
            print("ERROR: Could not get Token. Check AppID/AccessCode in SystemConfig.")
            return

        print(f"Token: {token[:10]}...")
        
        # Test Fetch Account Objects (Type 1)
        print("Fetching Account Objects (limit 5)...")
        data = service.client.get_dictionary(data_type=1, skip=0, take=5)
        print(f"Items received: {len(data)}")
        
        if len(data) > 0:
            print("Sample Item 0:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
            
            # Check for Group Data
            item = data[0]
            g_ids = item.get('account_object_group_id_list')
            g_names = item.get('account_object_group_name_list')
            print(f"Group IDs: {g_ids}")
            print(f"Group Names: {g_names}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_sync()
