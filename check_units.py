
import requests
import json

def check_units():
    url = "http://localhost:8000/api/data/units"
    try:
        resp = requests.get(url)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Units Count: {len(data)}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_units()
