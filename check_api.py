
import requests
import json

def check_api():
    url = "http://localhost:8000/api/data/vendors?limit=20"
    try:
        resp = requests.get(url)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Total: {data.get('total')}")
            items = data.get('data', [])
            print(f"Count returned: {len(items)}")
            if items:
                print("--- First 3 Items ---")
                for item in items[:3]:
                    print(json.dumps(item, ensure_ascii=False))
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api()
