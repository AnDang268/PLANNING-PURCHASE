
import requests
import json
import time
from backend.database import SessionLocal
from backend.models import SystemConfig
from backend.amis_accounting_client import AmisAccountingClient

def debug_counts():
    with open("debug_counts_output.txt", "w", encoding="utf-8") as f:
        def log(msg):
            print(msg)
            try:
                f.write(str(msg) + "\n")
            except: pass

        db = SessionLocal()
        try:
            def get_config(key):
                cfg = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
                return cfg.config_value if cfg else None

            app_id = get_config('MISA_AMIS_ACT_APP_ID')
            access_code = get_config('MISA_AMIS_ACT_ACCESS_CODE')
            base_url = get_config('MISA_AMIS_ACT_BASE_URL') or "https://actapp.misa.vn"
            
            log(f"Config Loaded. AppID: {app_id}")
            
            client = AmisAccountingClient(app_id, access_code, "CÔNG TY TNHH KIÊN THÀNH TÍN", base_url)
            
            # Types to check
            # 1: Account Objects (Partners)
            # 2: Inventory Items (Products)
            # 3: Stock (Warehouses)
            # 4: Units
            # 14: Product Groups
            
            targets = [
                (1, "Account Objects (Partners)"),
                (2, "Inventory Items (Products)"),
                # (14, "Product Groups"),
            ]
            
            for dtype, dname in targets:
                log(f"\n--- Checking {dname} (Type {dtype}) ---")
                total_count = 0
                skip = 0
                take = 500 # Try larger batch
                page = 1
                
                while True:
                    log(f"  Page {page}: Fetching skip={skip}, take={take}...")
                    start_t = time.time()
                    try:
                        batch = client.get_dictionary(dtype, skip=skip, take=take)
                    except Exception as e:
                        log(f"  !!! API Error: {e}")
                        break
                        
                    dur = time.time() - start_t
                    count = len(batch) if batch else 0
                    log(f"    -> Got {count} items in {dur:.2f}s")
                    
                    if count == 0:
                        log("    -> Empty batch. Done.")
                        break
                        
                    total_count += count
                    skip += count
                    page += 1
                    
                    # Safety break
                    if page > 50: 
                        log("    -> Safety Limit Reached (50 pages). Breaking.")
                        break
                        
                log(f"=== TOTAL {dname}: {total_count} ===")

        finally:
            db.close()

if __name__ == "__main__":
    debug_counts()
