import requests
import json
from backend.main import MISA_APP_ID, MISA_ACCESS_KEY, MISA_BASE_URL

# 1. GET TOKEN (Works with User App ID)
auth_url = f"{MISA_BASE_URL.rstrip('/')}/api/v2/Account"
payload = {
    "client_id": MISA_APP_ID, # kttwebshop
    "client_secret": MISA_ACCESS_KEY
}

print(f"--- 1. Getting Token with {MISA_APP_ID} ---")
try:
    resp = requests.post(auth_url, json=payload, headers={"Content-Type": "application/json"})
    if resp.status_code != 200:
        print(f"[FAIL] Auth Status: {resp.status_code}")
        print(resp.text)
        exit()
    
    data = resp.json()
    if not data.get("success"):
        print(f"[FAIL] Auth Success=False: {data}")
        exit()
        
    token = data.get("data")
    print(f"[SUCCESS] Token: {token[:20]}...")

    # 2. TEST DATA FETCH WITH VARIOUS HEADERS
    print(f"\n--- 2. Testing Headers for 'companycode' error ---")
    product_url = f"{MISA_BASE_URL.rstrip('/')}/api/v2/Products?page=0&pageSize=1"
    
    headers_variations = [
        {"Authorization": f"Bearer {token}"}, # Baseline
        {"Authorization": f"Bearer {token}", "companycode": MISA_APP_ID},
        {"Authorization": f"Bearer {token}", "x-tenantid": MISA_APP_ID},
        {"Authorization": f"Bearer {token}", "CompanyCode": MISA_APP_ID},
        {"Authorization": f"Bearer {token}", "Appid": MISA_APP_ID},
        {"Authorization": f"Bearer {token}", "companycode": "kttwebshop"}, # Explicit literal
        {"Authorization": f"Bearer {token}", "x-misa-app-id": MISA_APP_ID}
    ]

    for h in headers_variations:
        label = str(h).replace(token, "TOKEN")
        print(f"\nTesting Headers: {label}")
        try:
            r = requests.get(product_url, headers=h)
            print(f"   Status: {r.status_code}")
            if r.status_code == 200:
                print(f"!!! WINNER FOUND !!!")
                print(f"Header: {h}")
                print(f"Data Count: {len(r.json().get('Data', []) or r.json().get('data', []) or [])}")
                break
            else:
                pass # print(f"   [FAIL] {r.text[:200]}")
        except Exception as e:
            print(f"   [ERROR] {e}")

except Exception as e:
    print(f"[CRITICAL ERROR] {e}")
