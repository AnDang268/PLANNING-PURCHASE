import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine, get_db
from backend.models import DimProducts

def verify_data():
    print(">>> Verifying Real MISA Data...")
    db = next(get_db())
    try:
        # Get one product 
        prod = db.query(DimProducts).first()
        if prod:
            print(f"Product Found: {prod.sku_id}")
            print(f"Name: {prod.product_name}")
            print(f"Name (Repr): {repr(prod.product_name)}")
            
            # Heuristic check for Vietnamese characters
            if any(ord(c) > 128 for c in prod.product_name):
                 print(">>> SUCCESS: Unicode characters detected.")
            else:
                 print(">>> WARNING: JSON/API might return plain ASCII or sync not finished.")
        else:
            print(">>> No Products found yet. Sync might still be running.")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_data()
