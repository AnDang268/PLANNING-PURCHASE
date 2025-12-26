
import requests
import json

def check_customers():
    url = "http://localhost:8000/api/data/customers"
    try:
        resp = requests.get(url)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('data', [])
            print(f"Customer Count returned: {len(items)}")
            if items:
                 print(f"Sample: {items[0]['customer_name']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_customers()
