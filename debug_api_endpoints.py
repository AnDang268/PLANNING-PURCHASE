import urllib.request
import json
import urllib.error

ENDPOINTS = [
    "http://localhost:8000/api/data/units",
    "http://localhost:8000/api/data/groups",
    "http://localhost:8000/api/data/profiles"
]

def check_endpoints():
    print("--- Checking API Endpoints ---")
    for url in ENDPOINTS:
        try:
            print(f"Checking: {url}")
            with urllib.request.urlopen(url) as response:
                print(f"  Status: {response.getcode()}")
                if response.getcode() == 200:
                    data = json.loads(response.read().decode())
                    count = len(data) if isinstance(data, list) else len(data.get('data', []))
                    print(f"  Success. Items: {count}")
                else:
                    print(f"  Failed with status: {response.getcode()}")
        except urllib.error.HTTPError as e:
            print(f"  HTTP Error: {e.code} - {e.reason}")
            print(f"  Content: {e.read().decode()}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    check_endpoints()
