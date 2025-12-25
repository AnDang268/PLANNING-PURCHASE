from backend.amis_accounting_client import AmisAccountingClient
from backend.database import SessionLocal
from backend.models import SystemConfig

# READ FROM DB
db = SessionLocal()
def get_conf(key):
    c = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    return c.config_value if c else None

APP_ID = get_conf("MISA_AMIS_ACT_APP_ID")
ACCESS_CODE = get_conf("MISA_AMIS_ACT_ACCESS_CODE")
ORG_CODE = get_conf("MISA_AMIS_ACT_ORG_CODE")
BASE_URL = get_conf("MISA_AMIS_ACT_BASE_URL")

db.close()

print(f"--- TESTING AMIS ACCOUNTING CLIENT (FROM DB CONFIG) ---")
print(f"AppID: {APP_ID[:5]}... | Org: {ORG_CODE}")

client = AmisAccountingClient(APP_ID, ACCESS_CODE, company_code=ORG_CODE, base_url=BASE_URL)

# 1. Test Auth
token = client.get_token()
if token:
    print(f"[OK] Token Generated: {token[:20]}...")
    
    # 2. Test Data Access with Org Code
    print(f"\n--- Testing Data Access with Org: {ORG_CODE} ---")
    
    # Try generic endpoint
    data = client.call_api("api/v1/AccountObject", method="GET")
    if data:
        print(f"   [SUCCESS] Data Fetched!")
        print(f"   Sample: {str(data)[:200]}")
    else:
        print("[FAIL] Data Fetch Failed (Check logs)")
else:
    print("[FAIL] Token Generation Failed")
