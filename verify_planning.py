
import requests

BASE_URL = "http://localhost:8000/api"

def verify_planning():
    print("1. Running Rolling Calculation to Ensure Needs...")
    # Ensure needs exist (Standard Profile)
    requests.post(f"{BASE_URL}/planning/rolling/run", json={"horizon_months": 6, "profile_id": "STD"})
    
    print("2. Generating Purchase Plans...")
    resp = requests.post(f"{BASE_URL}/planning/generate-plans")
    print(f"Generate Result: {resp.status_code}")
    print(resp.json())
    
    print("3. Fetching Plans...")
    resp = requests.get(f"{BASE_URL}/planning/plans?pending_only=true&limit=5")
    data = resp.json()
    print(f"Found {data['total']} plans.")
    for p in data['data']:
        print(f"Plan ID: {p['id']} - SKU: {p['sku_id']} - Qty: {p['suggested_quantity']} -> {p['final_quantity']} - Notes: {p['notes']}")

if __name__ == "__main__":
    verify_planning()
