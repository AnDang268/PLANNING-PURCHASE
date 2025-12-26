
from backend.database import SessionLocal
from backend.models import SystemConfig
from backend.amis_accounting_client import AmisAccountingClient
import json

def test_client():
    db = SessionLocal()
    try:
        def get_config(key):
            cfg = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
            return cfg.config_value if cfg else None

        app_id = get_config('MISA_AMIS_ACT_APP_ID')
        access_code = get_config('MISA_AMIS_ACT_ACCESS_CODE')
        base_url = get_config('MISA_AMIS_ACT_BASE_URL') or "https://actapp.misa.vn"
        
        client = AmisAccountingClient(app_id, access_code, "TEST", base_url)
        
        print("Fetching 1 batch of Vendors/Customers...")
        # Type 1 = Partners
        data = client.get_dictionary(1, skip=0, take=5)
        
        print(f"Got {len(data)} items.")
        for item in data:
            name = item.get("account_object_name", "N/A")
            code = item.get("account_object_code", "N/A")
            print(f"Code: {code}, Name: {name}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_client()
