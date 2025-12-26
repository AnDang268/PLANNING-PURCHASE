import requests
import json

BASE_URL = "http://localhost:8000"

def check_endpoint(endpoint):
    print(f"--- Checking {endpoint} ---")
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and 'data' in data:
                print(f"Count: {len(data['data'])}")
                if len(data['data']) > 0:
                    item = data['data'][0]
                    # Print raw representation of Name to check encoding
                    if 'vendor_name' in item:
                        print(f"Name Repr: {repr(item['vendor_name'])}")
                    elif 'customer_name' in item:
                        print(f"Name Repr: {repr(item['customer_name'])}")
                    print("Sample:", json.dumps(item, indent=2, ensure_ascii=False))
                else:
                    print("Data is empty list.")
            elif isinstance(data, list):
                print(f"Count: {len(data)}")
                if len(data) > 0:
                    print("Sample:", json.dumps(data[0], indent=2))
                else:
                    print("Data is empty list.")
            else:
                print("Unknown structure:", str(data)[:100])
        else:
            print("Error:", resp.text)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_endpoint("/api/data/vendors")
    check_endpoint("/api/data/customers")
