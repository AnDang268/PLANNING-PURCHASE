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
# Login requires the Full Name
ORG_NAME = "CÔNG TY TNHH KIÊN THÀNH TÍN"
# Found Tenant Code
TENANT_CODE = "3X6710II" 

BASE_URL = "https://actapp.misa.vn"
db.close()

print(f"--- TESTING TENANT CODE: {TENANT_CODE} ---")
client = AmisAccountingClient(APP_ID, ACCESS_CODE, company_code=ORG_NAME, base_url=BASE_URL)

# 1. Login
token = client.get_token()
if not token:
    print("[FAIL] Login failed")
    exit()

# 2. Sync Request
URL = f"{BASE_URL}/apir/sync/actopen/get_dictionary"
PAYLOAD = {
    "app_id": APP_ID,
    "data_type": "Unit",
    "skip": 0,
    "take": 5
}
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
    "X-MISA-CompanyCode": TENANT_CODE,
    "CompanyCode": TENANT_CODE
}

try:
    print(f"POST {URL} ...")
    resp = requests.post(URL, json=PAYLOAD, headers=HEADERS, timeout=10)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"[SUCCESS] Got Data!")
        print(f"Keys: {list(data.keys())}")
        print(f"Data Sample: {str(data)[:200]}")
    else:
        print(f"[FAIL] {resp.status_code}")
        print(f"Body: {resp.text}")
except Exception as e:
    print(f"[ERR] {e}")
