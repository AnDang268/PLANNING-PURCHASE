
from backend.database import SessionLocal
from backend.models import DimVendors, DimCustomers

def check_counts():
    with open("counts_output.txt", "w", encoding="utf-8") as f:
        def log(msg):
            print(msg)
            f.write(str(msg) + "\n")
            
        db = SessionLocal()
        try:
            v_count = db.query(DimVendors).count()
            c_count = db.query(DimCustomers).count()
            
            log(f"DimVendors Count: {v_count}")
            log(f"DimCustomers Count: {c_count}")
            
            log("\n--- Sample Vendors (Top 5) ---")
            vendors = db.query(DimVendors).limit(5).all()
            for v in vendors:
                log(f"ID: {v.vendor_id}, Name: {v.vendor_name}, Group: {v.group_id}")

        finally:
            db.close()

if __name__ == "__main__":
    check_counts()
