
from backend.database import SessionLocal
from backend.models import SystemConfig, DimCustomerGroups
from backend.amis_accounting_client import AmisAccountingClient
import json
import uuid

def debug_group():
    db = SessionLocal()
    try:
        def get_config(key):
            cfg = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
            return cfg.config_value if cfg else None

        app_id = get_config('MISA_AMIS_ACT_APP_ID')
        access_code = get_config('MISA_AMIS_ACT_ACCESS_CODE')
        base_url = get_config('MISA_AMIS_ACT_BASE_URL') or "https://actapp.misa.vn"
        
        client = AmisAccountingClient(app_id, access_code, "TEST", base_url)
        
        print("Fetching 1 batch to find a Group Name...")
        batch = client.get_dictionary(1, skip=0, take=50) # fetch enough to find one with group
        
        target_name = None
        target_id = None
        
        for item in batch:
             names = item.get('account_object_group_name_list')
             ids = item.get('account_object_group_id_list')
             if names and "ố" in names or "ấ" in names or "ư" in names: # Find one with special chars
                 print(f"FOUND RAW containing special chars: {names}")
                 target_name = names.split(';')[0]
                 target_id = ids.split(';')[0] if ids else f"TEST_{uuid.uuid4().hex}"
                 break
        
        if not target_name:
            print("Could not find a group with special chars in first 50. Using manual test.")
            target_name = "TEST GRP Trường Giang Cấp 1"
            target_id = f"TEST_GRP_{uuid.uuid4().hex[:6]}"
            
        print(f"Attempting to Insert: {target_name} (ID: {target_id})")
        
        # Insert
        obj = DimCustomerGroups(group_id=target_id, group_name=target_name)
        db.merge(obj)
        db.commit()
        print("Inserted.")
        
        # Read Back
        read_obj = db.query(DimCustomerGroups).filter(DimCustomerGroups.group_id == target_id).first()
        print(f"READ BACK: {read_obj.group_name}")
        
        print(f"Raw bytes of read string: {[ord(c) for c in read_obj.group_name]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_group()
