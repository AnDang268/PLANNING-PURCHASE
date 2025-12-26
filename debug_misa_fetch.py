
import json
import os
import sys

sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import SystemConfig
from backend.misa_crm_v2_client import MisaCrmV2Client

def debug_fetch():
    db = SessionLocal()
    try:
        def get_conf(k):
            c = db.query(SystemConfig).filter(SystemConfig.config_key == k).first()
            return c.config_value if c else None

        client_id = get_conf('MISA_CRM_CLIENT_ID')
        client_secret = get_conf('MISA_CRM_CLIENT_SECRET')
        company_code = get_conf('MISA_CRM_COMPANY_CODE')

        print(f"Config: {client_id}, {company_code}, SecretLen={len(client_secret) if client_secret else 0}")

        client = MisaCrmV2Client(client_id, client_secret, company_code)
        print("Fetching Product Ledger...")
        items = client.get_product_ledger(page=1, page_size=5)
        
        print(f"Items Count: {len(items)}")
        
        with open('misa_data.json', 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
            
        print("Data saved to misa_data.json")

    except Exception as e:
        print(f"ERROR: {repr(e).encode('ascii', 'replace').decode()}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_fetch()
