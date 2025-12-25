from backend.amis_accounting_client import AmisAccountingClient
from backend.database import SessionLocal
from backend.models import SystemConfig
import json

# READ CONFIG
db = SessionLocal()
def get_conf(key):
    c = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    return c.config_value if c else None

APP_ID = get_conf("MISA_AMIS_ACT_APP_ID")
ACCESS_CODE = get_conf("MISA_AMIS_ACT_ACCESS_CODE")
ORG_CODE = get_conf("MISA_AMIS_ACT_ORG_CODE")
BASE_URL = get_conf("MISA_AMIS_ACT_BASE_URL")
db.close()

import requests

print("--- TESTING DICTIONARY SYNC (MULTI-HOST) ---")
client = AmisAccountingClient(APP_ID, ACCESS_CODE, company_code=ORG_CODE, base_url=BASE_URL)
token = client.get_token()

if token:
    payload = {
        "app_id": APP_ID,
        "data_type": "Unit", # Try checking Unit first (Simpler)
        "skip": 0,
        "take": 10,
        "last_sync_time": ""
    }
    
    HOSTS = [
        "https://actapp.misa.vn", # Known Auth
        "https://act.misa.vn",    # Likely Data
        "https://amisplatform.misa.vn",
        "https://actapp.misa.vn/apir" # Maybe path issue?
    ]
    
    for host in HOSTS:
        url = f"{host}/apir/sync/actopen/get_dictionary" # Standard path from docs
        print(f"\n>>> POST {url}")
        headers = client._get_headers()
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            print(f"   Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"   [SUCCESS] {resp.text[:300]}")
            else:
                print(f"   [FAIL] {resp.text[:300]}")
        except Exception as e:
            print(f"   [ERR] {e}")
else:
    print("[FAIL] No Token")
