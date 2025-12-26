
import warnings
from sqlalchemy import exc as sa_exc

# Suppress warnings
warnings.simplefilter("ignore", category=sa_exc.SAWarning)

from backend.database import SessionLocal
from backend.models import DimCustomers, DimVendors

def inspect_one():
    db = SessionLocal()
    try:
        print("--- INSPECTING START ---")
        customers = db.query(DimCustomers).all()
        print(f"Total Customers: {len(customers)}")
        # Print ALL IDs to see if they are from the end of the list
        for i, c in enumerate(customers):
            print(f"[{i}] {c.customer_id} - {c.customer_name}")
            
        vendors = db.query(DimVendors).all()
        print(f"Total Vendors: {len(vendors)}")
        for v in vendors:
            print(f"Vendor: {v.vendor_id} - {v.vendor_name}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_one()
