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
TENANT_CODE = "3X6710II" 
BASE_URL = "https://actapp.misa.vn"

db.close()

print(f"--- ENUM SCANNER ---")
client = AmisAccountingClient(APP_ID, ACCESS_CODE, company_code=ORG_NAME, base_url=BASE_URL)
token = client.get_token()

URL = f"{BASE_URL}/apir/sync/actopen/get_dictionary"
# Use validated headers from debug_dictionary_final.py
HEADERS = {
    "Content-Type": "application/json",
    "X-MISA-AccessToken": token
}

print(f"Token: {token[:10]}...")

for i in range(16, 41):
    payload = {
        "app_id": APP_ID,
        "data_type": i, # Numeric
        "skip": 0,
        "take": 5
    }
    try:
        resp = requests.post(URL, json=payload, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
             data = resp.json()
             if data.get("Success"):
                 raw_data = data.get("Data", [])
                 items = []
                 
                 if isinstance(raw_data, str):
                     try:
                         items = json.loads(raw_data)
                     except:
                         items = []
                         print(f"[WARN] Type {i}: Could not parse Data string.")
                 elif isinstance(raw_data, list):
                     items = raw_data
                 
                 count = len(items)
                 first_item = items[0] if count > 0 else {}
                 
                 if isinstance(first_item, dict):
                     keys = list(first_item.keys())
                     print(f"[FOUND] Type {i}: Count={count}")
                     print(f"   Keys: {keys}")
                     # Check specific columns
                     if "is_customer" in keys or "is_vendor" in keys:
                         print(f"   -> AccountObject? Cust={first_item.get('is_customer')}, Vend={first_item.get('is_vendor')}")
                     if "inventory_item_category_id" in keys:
                         print(f"   -> Product Group!")
                 else:
                     val = str(first_item)[:50]
                     print(f"[FOUND-RAW] Type {i}: Count={count}, Val={val}")
             else:
                 pass
        else:
             pass # HTTP Fail
    except Exception as e:
        print(f"[ERR Type {i}] {e}")

# Try Strings too
TYPES = ["Customer", "Vendor", "Employee", "InventoryItem", "Stock", "Unit", "OrganizationUnit"]
for t in TYPES:
    payload = {"app_id": APP_ID, "data_type": t, "skip": 0, "take": 5}
    try:
        resp = requests.post(URL, json=payload, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
             print(f"[SUCCESS] Type {t}: {resp.text[:200]}")
    except: pass
