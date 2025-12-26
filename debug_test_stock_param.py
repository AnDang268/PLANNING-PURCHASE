
import json
import os
import sys
import requests

sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import SystemConfig
from backend.misa_crm_v2_client import MisaCrmV2Client

def debug_stock_param():
    db = SessionLocal()
    try:
        def get_conf(k):
            c = db.query(SystemConfig).filter(SystemConfig.config_key == k).first()
            return c.config_value if c else None

        client_id = get_conf('MISA_CRM_CLIENT_ID')
        client_secret = get_conf('MISA_CRM_CLIENT_SECRET')
        company_code = get_conf('MISA_CRM_COMPANY_CODE')

        # Authenticate manually
        client = MisaCrmV2Client(client_id, client_secret, company_code)
        token = client.authenticate()
        
        url = f"{client.base_url}/Stocks/product_ledger"
        headers = {
            "authorization": f"Bearer {token}", 
            "clientid": client_id,
            "companycode": company_code
        }
        
        # Test 1: Using Stock Code "1111"
        print("Testing with Stock Code '1111'...")
        resp1 = requests.get(url, headers=headers, params={"page": 1, "pageSize": 1, "stockID": "1111"})
        print(f"Resp1: {resp1.status_code} - {resp1.text[:200]}")
        
        # Test 2: Using UUID from previous debug_stocks.json (needs checking, but let's try a likely one or just random to see error)
        # Better: let's fetch stocks first, pick one, and test both ID and Code
        print("Fetching Stocks first...")
        resp_stocks = requests.get(f"{client.base_url}/Stocks", headers=headers)
        stocks_data = resp_stocks.json().get("data", [])
        
        if stocks_data:
            first_stock = stocks_data[0]
            s_code = first_stock.get("stock_code")
            s_id = first_stock.get("stock_id") or first_stock.get("act_database_id") # MISA often uses act_database_id or stock_id
            
            print(f"Testing Stock: {s_code} / {s_id}")
            
            if s_id:
                print(f"Testing with Stock ID '{s_id}'...")
                resp2 = requests.get(url, headers=headers, params={"page": 1, "pageSize": 1, "stockID": s_id})
                print(f"Resp2: {resp2.status_code} - {resp2.text[:200]}")

    except Exception as e:
        print(f"ERROR: {repr(e).encode('ascii', 'replace').decode()}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_stock_param()
