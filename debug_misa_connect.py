from backend.misa_client import MisaClient
from backend.main import MISA_APP_ID, MISA_ACCESS_KEY, MISA_BASE_URL
import time

print(f"Testing Connection to: {MISA_BASE_URL}")
print(f"App ID: {MISA_APP_ID}")
print("Connecting...")

try:
    client = MisaClient(MISA_APP_ID, MISA_ACCESS_KEY, MISA_BASE_URL)
    
    start = time.time()
    # Fetch just 5 products to test speed
    data = client.get_products(page_index=1, page_size=5)
    end = time.time()
    
    if data:
        print(f"[SUCCESS] Connected in {end - start:.2f} seconds.")
        print(f"Received {len(data)} items.")
        if len(data) > 0:
            print("--- SAMPLE ITEM KEYS ---")
            print(data[0].keys())
            print("--- SAMPLE ITEM DATA ---")
            print(data[0])
    else:
        print("[WARNING] Connected but received NO data (Empty list).")

except Exception as e:
    print(f"\n[ERROR] Connection Failed: {str(e)}")
