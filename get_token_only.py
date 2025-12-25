import requests
import json

URL = "https://actapp.misa.vn/api/oauth/actopen/connect"
HEADERS = {"Content-Type": "application/json"}
PAYLOAD = {
    "app_id": "04991a48-9138-42a0-93a2-1a529c47f379",
    "access_code": "dIe3QQpQ6mWBumZyAoYKbIS8zcmfg+uJhqtmly1j+xAm2HbWqDn8dQb+Al+xc4cluMwLZdqeCN9eiPaJGHRssGy8YRw5nxQZop/CVCOS2+jcnTuXzq4XrRD9233iMFzVk+UNMtx+nSLKmOh0ogovywSCFmDqolVainCotUD/Ny+YK9PV6kMGRSOiD7SJZIsOAqi56OJCIIRB077X47Aw0hEoauBlfUYIn/tOu2G1Lo+AyXz8fMNj0YgpcAMfd5eDFgeuVOf9mHeRi2xaTpuksg==",
    "org_company_code": "CÔNG TY TNHH KIÊN THÀNH TÍN"
}

resp = requests.post(URL, json=PAYLOAD, headers=HEADERS)
if resp.status_code == 200:
    data = resp.json()
    if data.get("Data"):
        inner = json.loads(data["Data"])
        print(inner.get("access_token"))
    else:
        print("No Data field")
else:
    print(f"Error: {resp.status_code}")
