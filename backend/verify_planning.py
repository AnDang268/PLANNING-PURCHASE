
import requests
import json

BASE_URL = "http://localhost:8000/api/planning"

def test_endpoints():
    print("Testing Planning Engine APIs...")
    
    # 1. Test Safety Stock Calculation
    try:
        print("1. Calling /calculate-safety-stock...")
        res = requests.post(f"{BASE_URL}/calculate-safety-stock", proxies={"http": None, "https": None})
        if res.status_code == 200:
            print(f"✅ Success: {res.json()}")
        else:
            print(f"❌ Failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 2. Test Plan Generation
    try:
        print("\n2. Calling /generate-plans...")
        res = requests.post(f"{BASE_URL}/generate-plans", proxies={"http": None, "https": None})
        if res.status_code == 200:
            print(f"✅ Success: {res.json()}")
        else:
            print(f"❌ Failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoints()
