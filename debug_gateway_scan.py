import requests
from backend.amis_accounting_client import AmisAccountingClient
from backend.database import SessionLocal
from backend.models import SystemConfig

# READ CONFIG
db = SessionLocal()
def get_conf(key):
    c = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    return c.config_value if c else None

APP_ID = get_conf("MISA_AMIS_ACT_APP_ID")
ACCESS_CODE = get_conf("MISA_AMIS_ACT_ACCESS_CODE")
ORG_CODE = get_conf("MISA_AMIS_ACT_ORG_CODE")

print("--- AUTHENTICATING ---")
# Use the known working Auth Endpoint
client = AmisAccountingClient(APP_ID, ACCESS_CODE, company_code=ORG_CODE, base_url="https://actapp.misa.vn")
token = client.get_token()

if not token:
    print("[FAIL] Could not get Token.")
    exit()

TOKEN = client.token
HEADERS = {
    "Content-Type": "application/json",
    "X-MISA-CompanyCode": ORG_CODE,
    "CompanyCode": ORG_CODE # Try both
}

HOSTS = [
    "https://actapp.misa.vn",
    "https://act.misa.vn",
    "https://amisplatform.misa.vn"
]

TESTS = [
    {
        "name": "RPC get_dictionary",
        "method": "POST",
        "path": "/apir/sync/actopen/get_dictionary",
        "json": {
            "app_id": APP_ID,
            "data_type": "Unit",
            "skip": 0,
            "take": 5
        }
    },
    {
        "name": "REST Unit",
        "method": "GET",
        "path": "/api/v1/Unit",
        "json": None
    },
    {
        "name": "REST InventoryItem",
        "method": "GET",
        "path": "/api/v1/InventoryItem",
        "json": None
    }
]

import sys

print("\n--- SCANNING GATEWAYS ---")
with open("scan_log.txt", "w", encoding="utf-8") as log_file:
    def log(msg):
        print(msg)
        log_file.write(msg + "\n")
        
    for host in HOSTS:
        log(f"\n--- HOST: {host} ---")
        for t in TESTS:
            url = host + t["path"]
            log(f"   > Test: {t['name']} ({url})")
            try:
                if t["method"] == "POST":
                    resp = requests.post(url, json=t["json"], headers=HEADERS, timeout=10)
                else:
                    resp = requests.get(url, headers=HEADERS, timeout=10)
                
                log(f"     Status: {resp.status_code}")
                if resp.status_code == 200:
                    log(f"     [SUCCESS] Body: {resp.text[:300]}")
                else:
                    log(f"     [FAIL] Body: {resp.text[:100]}")
            except Exception as e:
                log(f"     [ERR] {e}")
    log("--- SCAN COMPLETE ---")
