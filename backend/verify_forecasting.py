
import requests
import json

BASE_URL = "http://localhost:8000/api/planning/forecast"
PROXIES = {"http": None, "https": None} # Bypass local proxy

def test_forecasting():
    print("Testing Forecasting Engine APIs...")
    
    # Needs a real SKU to work. Let's fetch one first.
    try:
        products_res = requests.get("http://localhost:8000/api/data/products", proxies=PROXIES)
        if products_res.status_code != 200:
            print(f"❌ Failed to fetch products. Status: {products_res.status_code}")
            print(f"Response: {products_res.text}")
            return
            
        products = products_res.json()
        if not products:
            # Check structure, maybe it's {"data": [...], "total": N}
            # Wait, api/data/products returns {"data": [...]}
            # Let's check products_res.json() content first
            print("Response JSON:", products_res.json())
            return
            print("⚠️ No products found to test.")
            return

        # Handle paged response structure {"data": [...]}
        product_list = products.get("data", []) if isinstance(products, dict) else products
        if not product_list:
             print("⚠️ No products list found.")
             return

        sku_id = product_list[0]['sku_id']
        print(f"Using SKU: {sku_id}")
        
        # 1. Trigger Forecast (SMA)
        print("\n1. Triggering Forecast (SMA)...")
        payload = {"sku_id": sku_id, "model": "SMA", "periods": 15}
        res = requests.post(BASE_URL, json=payload, proxies=PROXIES)
        
        if res.status_code == 200:
            print(f"✅ Success: {res.json()}")
        else:
            print(f"❌ Failed: {res.text}")

        # 2. Get Forecast Data
        print(f"\n2. getting Forecast Data for {sku_id}...")
        res = requests.get(f"{BASE_URL}/{sku_id}", proxies=PROXIES)
        
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Success: Retrieved {len(data)} records")
            # Print last 3 records
            print("Last 3 records:", json.dumps(data[-3:], indent=2))
        else:
            print(f"❌ Failed: {res.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_forecasting()
