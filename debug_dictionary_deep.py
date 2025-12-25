import requests
import json
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
BASE_URL = get_conf("MISA_AMIS_ACT_BASE_URL") or "https://actapp.misa.vn"
db.close()

print("\n--- DEEP DEBUG: DICTIONARY SYNC ---")
client = AmisAccountingClient(APP_ID, ACCESS_CODE, company_code=ORG_CODE, base_url=BASE_URL)
token = client.get_token()

if not token:
    print("[FAIL] No Token!")
    exit()

URL = f"{BASE_URL}/apir/sync/actopen/get_dictionary"
HEADERS = client._get_headers()

# Permutations to test
PAYLOADS = [
    {
        "name": "OrganizationUnit (Snake)",
        "json": {"app_id": APP_ID, "data_type": "OrganizationUnit", "skip": 0, "take": 5}
    },
     {
        "name": "OrganizationUnit (Camel)",
        "json": {"appId": APP_ID, "dataType": "OrganizationUnit", "skip": 0, "take": 5}
    }
]

for p in PAYLOADS:
    print(f"\n--- Test: {p['name']} ---")
    
    # header tests
    TEST_HEADERS = [
        {"name": "Original (Unicode)", "val": ORG_CODE},
        {"name": "ASCII (Simple)", "val": "KTT_COMPANY"},
        {"name": "ASCII (User provided key?)", "val": "kttwebshop"} # Reuse CRM code?
    ]

    for h in TEST_HEADERS:
        current_headers = HEADERS.copy()
        try:
             # Force encode/decode to catch python header injection errors early
             val = h['val']
             current_headers["X-MISA-CompanyCode"] = val
             current_headers["CompanyCode"] = val
             
             print(f"   [HEADER] Testing with {h['name']}: {val}")
             resp = requests.post(URL, json=p['json'], headers=current_headers, timeout=10)
             print(f"   Status: {resp.status_code}")
             if resp.status_code == 200:
                print(f"   [SUCCESS] {resp.text[:300]}")
                break 
             elif resp.status_code == 400:
                 print(f"   [FAIL 400] Body: {resp.text[:200]}")
        except Exception as e:
            print(f"   [ERR] with {h['name']}: {e}")
