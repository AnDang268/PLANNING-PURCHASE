from backend.database import SessionLocal
from backend.models import DimVendors, DimCustomers
import traceback
import sys

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def test_query():
    print("Connecting to DB...")
    db = SessionLocal()
    try:
        print("Querying DimVendors...")
        vendors = db.query(DimVendors).all()
        print(f"Vendors Count: {len(vendors)}")
        if vendors:
            print(f"Sample Vendor: {vendors[0].vendor_name}")

        print("Querying DimCustomers...")
        customers = db.query(DimCustomers).all()
        print(f"Customers Count: {len(customers)}")
    except Exception:
        print("CRITICAL ERROR:")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_query()
