
import json
import os
import sys
import requests

sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import SystemConfig
from backend.misa_crm_v2_client import MisaCrmV2Client

def debug_stocks():
    db = SessionLocal()
    try:
        def get_conf(k):
            c = db.query(SystemConfig).filter(SystemConfig.config_key == k).first()
            return c.config_value if c else None

        client_id = get_conf('MISA_CRM_CLIENT_ID')
        client_secret = get_conf('MISA_CRM_CLIENT_SECRET')
        company_code = get_conf('MISA_CRM_COMPANY_CODE')
        
        print(f"Conf: {client_id}, {company_code}")

        # Authenticate manually to use client token
        client = MisaCrmV2Client(client_id, client_secret, company_code)
        token = client.authenticate()
        
        url = f"{client.base_url}/Stocks"
        headers = {
            "authorization": f"Bearer {token}", 
            "clientid": client_id,
            "companycode": company_code
        }
        
        print(f"Fetching Stocks from {url}...")
        resp = requests.get(url, headers=headers)
        
        print(f"Status: {resp.status_code}")
        try:
             data = resp.json()
             if data.get("success") or data.get("code") == 0:
                 items = data.get("data", [])
                 print(f"Stocks Found: {len(items)}")
                 if len(items) > 0:
                     print(f"First Stock: {str(items[0]).encode('ascii', 'replace').decode()}")
                 
                 with open("debug_stocks.json", "w", encoding="utf-8") as f:
                     json.dump(items, f, indent=2, ensure_ascii=False)
             else:
                 print(f"API API Error: {data}")
        except Exception as e:
            print(f"Parse Error: {e}")
            print(f"Raw: {resp.text.encode('ascii', 'replace').decode()}")

    except Exception as e:
        print(f"ERROR: {repr(e).encode('ascii', 'replace').decode()}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_stocks()
