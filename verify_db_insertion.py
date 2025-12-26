from backend.database import SessionLocal, engine
from backend.models import DimVendors, DimCustomers

def verify_unicode():
    db = SessionLocal()
    try:
        print("\n--- CHECKING VENDORS (Top 5) ---")
        vendors = db.query(DimVendors).limit(5).all()
        for v in vendors:
            print(f"Vendor: {v.vendor_name} (ID: {v.vendor_id})")

        print("\n--- CHECKING CUSTOMERS (Top 5) ---")
        customers = db.query(DimCustomers).limit(5).all()
        for c in customers:
            print(f"Customer: {c.customer_name} (ID: {c.customer_id})")

    finally:
        db.close()

if __name__ == "__main__":
    verify_unicode()
