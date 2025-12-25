import requests
import json
from backend.main import MISA_APP_ID, MISA_ACCESS_KEY, MISA_BASE_URL

URL = f"{MISA_BASE_URL.rstrip('/')}/api/v2/Account"

def test_auth(cid, secret, label):
    print(f"\n--- TESTING: {label} ---")
    print(f"ClientID: {cid}")
    print(f"Secret:   {secret[:10]}...")
    
    payload = {
        "client_id": cid,
        "client_secret": secret
    }
    
    try:
        resp = requests.post(URL, json=payload, headers={"Content-Type": "application/json"})
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                print("[SUCCESS] TOKEN RECEIVED!")
                print(f"Token: {data.get('data')[:20]}...")
                
                # TEST FETCH PRODUCT
                token = data.get('data')
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                print("   > Fetching 1 Product...")
                prod_resp = requests.get(f"{MISA_BASE_URL.rstrip('/')}/api/v2/Products?page=0&pageSize=1", headers=headers)
                print(f"   > Product Status: {prod_resp.status_code}")
                if prod_resp.status_code == 200:
                    prod_data = prod_resp.json()
                    # Handle Wrapper
                    if isinstance(prod_data, dict) and "Data" in prod_data: items = prod_data["Data"]
                    elif isinstance(prod_data, dict) and "data" in prod_data: items = prod_data["data"]
                    else: items = prod_data

                    if items and len(items) > 0:
                        print("   > KEYS FOUND:", list(items[0].keys()))
                    else:
                        print("   > NO PRODUCTS FOUND")
                return True
            else:
                print(f"[FAILED] Logic Error: {data}")
        else:
            print(f"[FAILED] HTTP Error: {resp.text}")
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
    return False

# 1. Try with User's App ID
test_auth(MISA_APP_ID, MISA_ACCESS_KEY, "User App ID (kttwebshop)")

# 2. Try with 'PublicAPI' (Doc Example)
test_auth("PublicAPI", MISA_ACCESS_KEY, "Doc Example (PublicAPI)")
