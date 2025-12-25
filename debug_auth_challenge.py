import requests
import json

URL = "https://actapp.misa.vn/api/oauth/actopen/connect"
HEADERS = {"Content-Type": "application/json"}

PAYLOAD = {
    "app_id": "04991a48-9138-42a0-93a2-1a529c47f379",
    "access_code": "dIe3QQpQ6mWBumZyAoYKbIS8zcmfg+uJhqtmly1j+xAm2HbWqDn8dQb+Al+xc4cluMwLZdqeCN9eiPaJGHRssGy8YRw5nxQZop/CVCOS2+jcnTuXzq4XrRD9233iMFzVk+UNMtx+nSLKmOh0ogovywSCFmDqolVainCotUD/Ny+YK9PV6kMGRSOiD7SJZIsOAqi56OJCIIRB077X47Aw0hEoauBlfUYIn/tOu2G1Lo+AyXz8fMNj0YgpcAMfd5eDFgeuVOf9mHeRi2xaTpuksg==",
    "org_company_code": "CÔNG TY TNHH KIÊN THÀNH TÍN"
}

print(f"--- TESTING AUTH (Unicode Payload) ---")
print(f"URL: {URL}")
json_body = json.dumps(PAYLOAD, ensure_ascii=False)
print(f"RAW JSON BODY: {json_body}") 

try:
    resp = requests.post(URL, json=PAYLOAD, headers=HEADERS, timeout=30)
    
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"Response Keys: {list(data.keys())}")
        if data.get("Data"):
             try:
                 inner = json.loads(data["Data"])
                 print("--- AUTH DATA ---")
                 print(json.dumps(inner, indent=2, ensure_ascii=False))
             except:
                 print(f"Data Raw: {data['Data']}")
        
        if data.get("Success"):
            print("[SUCCESS] Token retrieved.")
        else:
            print(f"[FAIL] API Error: {data.get('ErrorMessage')}")
except Exception as e:
    print(f"[ERR] Exception: {e}")
