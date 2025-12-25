import requests
import json
import base64
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
BASE_URL = "https://actapp.misa.vn"
db.close()

def decode_jwt(token):
    try:
        parts = token.split(".")
        if len(parts) < 2: return "Not a JWT"
        payload = parts[1]
        # Pad base64
        payload += "=" * ((4 - len(payload) % 4) % 4)
        decoded = base64.b64decode(payload).decode("utf-8")
        return json.loads(decoded)
    except Exception as e:
        return f"Decode Error: {e}"

print(f"--- TOKEN SCOPE DEBUG ---")
client = AmisAccountingClient(APP_ID, ACCESS_CODE, company_code=ORG_NAME, base_url=BASE_URL)
token = client.get_token()

if not token:
    print("[FAIL] No Token")
    exit()

print("\n> Token Claims:")
try:
    claims = decode_jwt(token)
    print(json.dumps(claims, indent=2))
except:
    print("Could not decode.")

print("\n> Testing Alternate Endpoints (Data Verification):")
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

# 1. Get Tenant Info (If exists)
URL_INFO = f"{BASE_URL}/api/oauth/actopen/get_tenant_info" # Guessing endpoint based on naming
try:
    print(f"POST {URL_INFO}")
    resp = requests.post(URL_INFO, headers=HEADERS, json={"app_id": APP_ID}, timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text[:200]}")
except Exception as e:
    print(f"[ERR] {e}")

# 2. Get User Profile?
URL_USER = f"{BASE_URL}/api/v1/User/GetCurrent"
try:
    print(f"GET {URL_USER}")
    resp = requests.get(URL_USER, headers=HEADERS, timeout=10)
    print(f"Status: {resp.status_code}")
except Exception as e:
    print(f"[ERR] {e}")
