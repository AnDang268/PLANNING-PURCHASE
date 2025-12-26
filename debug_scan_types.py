
from backend.database import SessionLocal
from backend.models import SystemConfig
from backend.amis_accounting_client import AmisAccountingClient
import json

def debug_scan():
    db = SessionLocal()
    try:
        def get_config(key):
            cfg = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
            return cfg.config_value if cfg else None

        app_id = get_config('MISA_AMIS_ACT_APP_ID')
        access_code = get_config('MISA_AMIS_ACT_ACCESS_CODE')
        base_url = get_config('MISA_AMIS_ACT_BASE_URL') or "https://actapp.misa.vn"
        
        client = AmisAccountingClient(app_id, access_code, "TEST", base_url)
        
        print("Scaning all items (Type 1) for flags...")
        
        skip = 0
        take = 500
        stats = {
            "total": 0,
            "is_customer_true": 0,
            "is_vendor_true": 0,
            "both_true": 0,
            "neither_true": 0,
            "keys_seen": set()
        }
        
        while True:
            print(f"Fetching {skip}...")
            batch = client.get_dictionary(1, skip=skip, take=take)
            if not batch: break
            
            for item in batch:
                stats["total"] += 1
                is_c = item.get("is_customer")
                is_v = item.get("is_vendor")
                
                code = item.get("account_object_code")
                if code:
                    stats["keys_seen"].add(code)

                # Check for alternative casings if main missing
                if is_c is None: is_c = item.get("IsCustomer")
                if is_v is None: is_v = item.get("IsVendor")
                
                if is_c: stats["is_customer_true"] += 1
                if is_v: stats["is_vendor_true"] += 1
                if is_c and is_v: stats["both_true"] += 1
                if not is_c and not is_v: stats["neither_true"] += 1
                
                # Sample keys from first invalid item
                if not is_c and not is_v and stats["neither_true"] == 1:
                     print("Sample NEITHER item keys:", item.keys())
                     print("Sample NEITHER item dump:", json.dumps(item, indent=2, ensure_ascii=False))

            skip += len(batch)
            if len(batch) < take: break
            
        print("\n--- STATS ---")
        stats["unique_codes"] = len(stats["keys_seen"])
        stats["keys_seen"] = "set()" # Clear for print
        print(json.dumps(stats, indent=2, default=str))
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_scan()
