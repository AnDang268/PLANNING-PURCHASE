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

print(f"--- PAYLOAD SCANNER ---")
client = AmisAccountingClient(APP_ID, ACCESS_CODE, company_code=ORG_NAME, base_url=BASE_URL)
token = client.get_token()

URL = f"{BASE_URL}/apir/sync/actopen/get_dictionary"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
    "X-MISA-CompanyCode": TENANT_CODE,
    "CompanyCode": TENANT_CODE
}

PAYLOADS = [
    # 1. Minimal / Empty
    {"name": "Empty Dict", "json": {}},
    
    # 2. Key variations
    {"name": "Unit no AppID", "json": {"data_type": "Unit", "skip": 0, "take": 5}},
    {"name": "Unit with branch null", "json": {"app_id": APP_ID, "data_type": "Unit", "branch_id": None, "skip": 0, "take": 5}},
    
    # 3. Data Type variations
    {"name": "Stock", "json": {"app_id": APP_ID, "data_type": "Stock", "skip": 0, "take": 5}},
    {"name": "InventoryItemCategory", "json": {"app_id": APP_ID, "data_type": "InventoryItemCategory", "skip": 0, "take": 5}},
    {"name": "Account", "json": {"app_id": APP_ID, "data_type": "Account", "skip": 0, "take": 5}},
    {"name": "Department", "json": {"app_id": APP_ID, "data_type": "Department", "skip": 0, "take": 5}},
    
    # 4. Old Schema?
    {"name": "SyncTime only", "json": {"app_id": APP_ID, "data_type": "Unit", "last_sync_time": ""}},
    
    # 5. Using branch_id explicitly if I can guess it? No.
]

for p in PAYLOADS:
    try:
        print(f"\n> Test: {p['name']}")
        
        # Test 1: Standard Headers
        resp = requests.post(URL, json=p['json'], headers=HEADERS, timeout=10)
        if resp.status_code == 200:
             print(f"  [SUCCESS] {resp.text[:300]}")
             break
        else:
             print(f"  [FAIL Std] {resp.status_code} {resp.text[:100]}")

        # Test 2: With X-MISA-AccessToken
        headers_v2 = HEADERS.copy()
        headers_v2["X-MISA-AccessToken"] = token 
        try:
             resp = requests.post(URL, json=p['json'], headers=headers_v2, timeout=10)
             if resp.status_code == 200:
                  print(f"  [SUCCESS V2] {resp.text[:300]}")
                  break
        except: pass

        # Test 3: Brute Force Headers (CRM pattern?)
        headers_v3 = HEADERS.copy()
        headers_v3["clientid"] = APP_ID # CRM uses client_id?
        headers_v3["X-MISA-BranchId"] = TENANT_CODE
        try:
             resp = requests.post(URL, json=p['json'], headers=headers_v3, timeout=10)
             if resp.status_code == 200:
                  print(f"  [SUCCESS V3] {resp.text[:300]}")
                  break
        except: pass
             
    except Exception as e:
        print(f"  [ERR] {e}")
