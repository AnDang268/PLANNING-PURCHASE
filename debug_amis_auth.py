import requests
import json

# NEW CREDENTIALS (AMIS ACT)
APP_ID = "04991a48-9138-42a0-93a2-1a529c47f379"
ACCESS_CODE = "dIe3QQpQ6mWBumZyAoYKbIS8zcmfg+uJhqtmly1j+xAm2HbWqDn8dQb+Al+xc4cluMwLZdqeCN9eiPaJGHRssGy8YRw5nxQZop/CVCOS2+jcnTuXzq4XrRD9233iMFzVk+UNMtx+nSLKmOh0ogovywSCFmDqolVainCotUD/Ny+YK9PV6kMGRSOiD7SJZIsOAqi56OJCIIRB077X47Aw0hEoauBlfUYIn/tOu2G1Lo+AyXz8fMNj0YgpcAMfd5eDFgeuVOf9mHeRi2xaTpuksg=="

# Potential Endpoints - Narrowed Down
ENDPOINTS = [
    "https://actapp.misa.vn/api/oauth/actopen/connect"
]

def test_auth(url):
    print(f"\n--- Testing Endpoint: {url} ---")
    
    # Payload Structure Guesses
    payloads = [
         {
            "appid": APP_ID, 
            "access_code": ACCESS_CODE
        },
        {
            "appId": APP_ID, # Camel Case (Most Likely)
            "accessCode": ACCESS_CODE
        },
         {
            "app_id": APP_ID, 
            "access_code": ACCESS_CODE
        }
    ]

    for p in payloads:
        try:
            print(f"   > Payload Keys: {list(p.keys())}")
            resp = requests.post(url, json=p, headers={"Content-Type": "application/json"}, timeout=10)
            print(f"   > Status: {resp.status_code}")
            try:
                data = resp.json()
                print(f"   > Body: {data}")
                if data.get("Success") == True or data.get("success") == True or "Token" in data:
                    print(f"!!! SUCCESS PAYLOAD: {list(p.keys())} !!!")
                    print(f"!!! TOKEN DATA: {data} !!!")
                    return True
            except:
                print(f"   > Body (Raw): {resp.text[:200]}")
        except Exception as e:
            print(f"   [ERROR] {e}")
    return False

print("--- STARTING AMIS ACCOUNTING DISCOVERY ---")
for ep in ENDPOINTS:
    if test_auth(ep):
        print(f"!!! FOUND WORKING ENDPOINT: {ep} !!!")
        break
