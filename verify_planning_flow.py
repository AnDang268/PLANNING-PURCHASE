
import requests
import json

BASE_URL = "http://localhost:8001"

def test_generate_plans():
    print(">>> 1. Triggering Plan Generation...")
    try:
        response = requests.post(f"{BASE_URL}/api/planning/generate-plans")
        response.raise_for_status()
        print("Success:", response.json())
    except Exception as e:
        print("FAILED to generate plans:", e)
        # return

def test_get_plans():
    print("\n>>> 2. Fetching Generated Plans...")
    try:
        response = requests.get(f"{BASE_URL}/api/planning/plans?limit=5")
        response.raise_for_status()
        data = response.json()
        print(f"Total Plans: {data.get('total')}")
        for p in data.get('data', []):
            print(f" - Plan #{p['id']}: SKU {p['sku_id']} | Sugg: {p['suggested_quantity']} | Status: {p['status']}")
    except Exception as e:
        print("FAILED to get plans:", e)

if __name__ == "__main__":
    test_generate_plans()
    test_get_plans()
