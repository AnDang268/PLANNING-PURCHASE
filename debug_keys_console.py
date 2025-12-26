
import json
import os
import sys

sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import SystemConfig
from backend.misa_crm_v2_client import MisaCrmV2Client

def debug_keys():
    db = SessionLocal()
    try:
        def get_conf(k):
            c = db.query(SystemConfig).filter(SystemConfig.config_key == k).first()
            return c.config_value if c else None

        client_id = get_conf('MISA_CRM_CLIENT_ID')
        client_secret = get_conf('MISA_CRM_CLIENT_SECRET')
        company_code = get_conf('MISA_CRM_COMPANY_CODE')
        
        print(f"Conf: {client_id}, {company_code}")

        client = MisaCrmV2Client(client_id, client_secret, company_code)
        
        # We need to bypass the debug logic inside client that prints/writes files
        # Actually client logic writes to debug_keys_final.txt
        # But we will use the return value
        
        print("Fetching...")
        items = client.get_product_ledger(page=1, page_size=1)
        print(f"Count: {len(items)}")
        
        if items:
            keys = list(items[0].keys())
            # SAFE PRINT
            print(f"KEYS_SAFE: {str(keys).encode('ascii', 'replace').decode()}")
            
            # Print first item sample safe
            print(f"ITEM_SAFE: {str(items[0]).encode('ascii', 'replace').decode()}")

    except Exception as e:
        print(f"ERROR: {repr(e).encode('ascii', 'replace').decode()}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_keys()
