import requests

try:
    resp = requests.get("http://localhost:8000/api/data/partner-groups")
    print(f"Status: {resp.status_code}")
    print("Body:")
    print(resp.text)
except Exception as e:
    print(e)
