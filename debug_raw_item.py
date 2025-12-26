
from backend.database import SessionLocal
from backend.models import SystemConfig
from backend.amis_accounting_client import AmisAccountingClient
import json

def debug_raw():
    db = SessionLocal()
    try:
        def get_config(key):
            cfg = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
            return cfg.config_value if cfg else None

        app_id = get_config('MISA_AMIS_ACT_APP_ID')
        access_code = get_config('MISA_AMIS_ACT_ACCESS_CODE')
        base_url = get_config('MISA_AMIS_ACT_BASE_URL') or "https://actapp.misa.vn"
        
        client = AmisAccountingClient(app_id, access_code, "TEST", base_url)
        
        print("Fetching 1 raw item...")
        # Type 1 = Partners
        data = client.get_dictionary(1, skip=0, take=1)
        
        if data:
            item = data[0]
            print(json.dumps(item, indent=2, ensure_ascii=False))
            print("\n--- KEY CHECK ---")
            print(f"is_customer: {item.get('is_customer')}")
            print(f"is_vendor: {item.get('is_vendor')}")
            print(f"IsCustomer: {item.get('IsCustomer')}")
            print(f"IsVendor: {item.get('IsVendor')}")
        else:
            print("No data returned.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_raw()
