
import json
import os
import sys
import requests

sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import SystemConfig
from backend.misa_crm_v2_client import MisaCrmV2Client

def debug_unit():
    db = SessionLocal()
    try:
        def get_conf(k):
            c = db.query(SystemConfig).filter(SystemConfig.config_key == k).first()
            return c.config_value if c else None

        client_id = get_conf('MISA_CRM_CLIENT_ID')
        client_secret = get_conf('MISA_CRM_CLIENT_SECRET')
        company_code = get_conf('MISA_CRM_COMPANY_CODE')

        client = MisaCrmV2Client(client_id, client_secret, company_code)
        
        print("Fetching one item to check unit keys...")
        items = client.get_product_ledger(page=1, page_size=1)
        
        if items:
            item = items[0]
            # Print all keys that look like 'unit'
            unit_keys = {k: v for k, v in item.items() if 'unit' in k.lower() or 'dvt' in k.lower()}
            print(f"Unit Keys Found: {str(unit_keys).encode('ascii', 'replace').decode()}")
            print(f"All Keys: {str(list(item.keys())).encode('ascii', 'replace').decode()}")
        else:
            print("No items returned.")

    except Exception as e:
        print(f"ERROR: {repr(e).encode('ascii', 'replace').decode()}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_unit()
