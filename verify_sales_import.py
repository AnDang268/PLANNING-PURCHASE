
import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"

def run_test():
    # 1. Upload Sales File
    print("Uploading Sales File...")
    # Using existing doc file
    file_path = r"d:\Document\SOURCE\PLANNING-PURCHASE\doc\So_chi_tiet_ban_hang.xlsx"
    
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        params = {'type': 'sales_details'}
        resp = requests.post(f"{BASE_URL}/data/import/upload", files=files, params=params)
        
    print(f"Upload Result: {resp.status_code}")
    print(resp.json())
    
    if resp.status_code != 200:
        print("Upload Failed. Stopping.")
        return

    # 2. Trigger Rolling Calculation
    print("\nTriggering Rolling Calculation...")
    # POST /api/planning/rolling/run  (Body: {})
    jsonData = {"horizon_months": 6, "profile_id": "STD"}
    resp = requests.post(f"{BASE_URL}/planning/rolling/run", json=jsonData)
    print(f"Calculation Result: {resp.status_code}")
    print(resp.json())

    # 3. Verify Output (Matrix)
    print("\nFetching Matrix (First 5)...")
    resp = requests.get(f"{BASE_URL}/planning/rolling/matrix?limit=5")
    data = resp.json()
    
    for item in data:
        print(f"SKU: {item['sku_id']}")
        for date_key, week in list(item['weeks'].items())[:4]:
            print(f"  Date: {date_key}, Open: {week['opening_stock']}, Closed: {week['closing']:.2f}, ActSold: {week.get('actual_sold', 'N/A')}")

if __name__ == "__main__":
    run_test()
