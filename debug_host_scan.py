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
# TENANT_CODE = "3X6710II" 
AUTH_URL_BASE = "https://actapp.misa.vn"

db.close()

print(f"--- HOST SCANNER ---")
# 1. Authenticate with Known Good Auth URL
client = AmisAccountingClient(APP_ID, ACCESS_CODE, company_code=ORG_NAME, base_url=AUTH_URL_BASE)
token = client.get_token()

if not token: 
    print("Auth Failed")
    exit()

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
    # "X-MISA-CompanyCode": TENANT_CODE # Try with/without
}

PAYLOAD = {"app_id": APP_ID, "data_type": "Unit", "skip": 0, "take": 5}

CANDIDATE_HOSTS = [
    "https://act.misa.vn",
    "https://amisplatform.misa.vn",
    "https://actapi.misa.vn",
    "https://api.misa.vn/act",
    "https://actapp.misa.vn" # Retry just in case
]

PATHS = [
    "/apir/sync/actopen/get_dictionary",
    "/api/v1/sync/actopen/get_dictionary"
]

for host in CANDIDATE_HOSTS:
    for path in PATHS:
        url = host + path
        try:
            print(f"> POST {url}")
            resp = requests.post(url, json=PAYLOAD, headers=HEADERS, timeout=5)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                 print(f"  [SUCCESS] {resp.text[:300]}")
                 break
            elif resp.status_code != 404:
                 print(f"  [ALIVE] {resp.status_code} Msg: {resp.text[:100]}")
        except Exception as e:
            print(f"  [ERR] {e}")
