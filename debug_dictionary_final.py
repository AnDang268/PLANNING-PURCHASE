import requests
import json
from backend.amis_accounting_client import AmisAccountingClient
from backend.database import SessionLocal
from backend.models import SystemConfig

# CONFIG
db = SessionLocal()
def get_conf(key):
    c = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    return c.config_value if c else None

APP_ID = get_conf("MISA_AMIS_ACT_APP_ID")
ACCESS_CODE = get_conf("MISA_AMIS_ACT_ACCESS_CODE")
ORG_NAME = "CÔNG TY TNHH KIÊN THÀNH TÍN"
BASE_URL = "https://actapp.misa.vn"
db.close()

print(f"--- FINAL DICTIONARY DEBUG ---")

# 1. Get Token (This part works)
client = AmisAccountingClient(APP_ID, ACCESS_CODE, company_code=ORG_NAME, base_url=BASE_URL)
token = client.get_token()
print(f"Token: {token[:20]}...")

# 2. Replicate User's cURL EXACTLY
URL = f"{BASE_URL}/apir/sync/actopen/get_dictionary"

# User's Headers: Only Content-Type and X-MISA-AccessToken. 
# NO Authorization. NO CompanyCode.
HEADERS = {
    "Content-Type": "application/json",
    "X-MISA-AccessToken": token 
}

# User's Payload
PAYLOAD = {
    "data_type": 4, # User used 4 (Maybe 'Customer' or 'Product'?)
    "skip": 0, 
    "take": 1000, 
    "app_id": APP_ID, 
    "last_sync_time": ""
}

try:
    print(f"\n> POST {URL}")
    print(f"Headers: {json.dumps(HEADERS, indent=2)}")
    print(f"Payload: {json.dumps(PAYLOAD, indent=2)}")
    
    resp = requests.post(URL, json=PAYLOAD, headers=HEADERS, timeout=30)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"[SUCCESS] Response Keys: {data.keys()}")
        if data.get("Success"):
             items = data.get("Data", [])
             print(f"Got {len(items)} items.")
             if items:
                 print(f"Sample Item: {items[0]}")
        else:
             print(f"[FAIL Logic] {data}")
    else:
        print(f"[FAIL HTTP] {resp.text}")

except Exception as e:
    print(f"[ERR] {e}")
