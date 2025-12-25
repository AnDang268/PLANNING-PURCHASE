import requests
import json

def trigger_sync():
    url = "http://localhost:8000/api/data/sync/misa"
    print(f"Triggering Sync: {url}")
    try:
        response = requests.post(url, timeout=300) # 5 min timeout for sync
        if response.status_code == 200:
            print("Sync Triggered Successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_sync()
