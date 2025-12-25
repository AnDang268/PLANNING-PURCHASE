
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/planning/rolling"

def test_rolling_api():
    print("Smoking Test: Rolling Supply Planning...")
    
    # 1. Trigger Calculation (Run for all SKUs)
    print("\n1. Triggering Calculation...")
    try:
        resp = requests.post(f"{BASE_URL}/run", json={"horizon_months": 12})
        if resp.status_code == 200:
            print("✅ Calculation Triggered Success:", resp.json())
        else:
            print("❌ Failed:", resp.text)
            return
    except Exception as e:
        print("❌ Error connecting to API:", e)
        return
        
    # Wait a bit for "processing" (although it's synchronous now)
    time.sleep(1)
    
    # 2. Fetch Matrix Data
    print("\n2. Fetching Matrix Data...")
    try:
        resp = requests.get(f"{BASE_URL}/matrix")
        if resp.status_code == 200:
            data = resp.json()
            count = len(data)
            print(f"✅ Success: Retrieved {count} inventory records.")
            if count > 0:
                print("Sample Record:", json.dumps(data[0], indent=2))
        else:
            print("❌ Failed:", resp.text)
    except Exception as e:
        print("❌ Error connecting to API:", e)

if __name__ == "__main__":
    test_rolling_api()
