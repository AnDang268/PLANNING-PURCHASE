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

print(f"--- PATH SCANNER ---")
client = AmisAccountingClient(APP_ID, ACCESS_CODE, company_code=ORG_NAME, base_url=BASE_URL)
token = client.get_token()

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
    "X-MISA-CompanyCode": TENANT_CODE,
    "CompanyCode": TENANT_CODE
}

PAYLOAD = {"app_id": APP_ID, "data_type": "Unit", "skip": 0, "take": 5}

PATHS = [
    "/apir/sync/actopen/get_dictionary",
    "/api/sync/actopen/get_dictionary", 
    "/api/actopen/sync/get_dictionary",
    "/actopen/sync/get_dictionary",
    "/api/v1/sync/actopen/get_dictionary",
    "/apir/actopen/sync/get_dictionary"
]

for path in PATHS:
    url = BASE_URL + path
    try:
        print(f"\n> POST {url}")
        resp = requests.post(url, json=PAYLOAD, headers=HEADERS, timeout=10)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
             print(f"  [SUCCESS] {resp.text[:300]}")
             break
        elif resp.status_code != 404: # 500 or 400 means path exists but request is bad
             print(f"  [FAIL] {resp.text[:100]}")
    except Exception as e:
        print(f"  [ERR] {e}")
