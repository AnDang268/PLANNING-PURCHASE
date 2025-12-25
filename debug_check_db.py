from backend.database import SessionLocal
from backend.models import DimProducts, DimVendors, FactSales
from sqlalchemy import text

print("--- DIAGNOSTIC DB CHECK ---")
try:
    db = SessionLocal()
    
    # 1. Check Connection
    db.execute(text("SELECT 1"))
    print("[OK] Database Connection")

    # 2. Count Records
    prod_count = db.query(DimProducts).count()
    vend_count = db.query(DimVendors).count()
    sale_count = db.query(FactSales).count()

    print(f"[DATA] Orders:   {sale_count}")

    print("\n--- SAMPLE REAL DATA (PROOF) ---")
    try:
        samples = db.query(DimProducts).limit(5).all()
        for s in samples:
            print(f"SKU: {s.sku_id} | Name: {s.product_name}")
    except Exception as ie:
        print(f"[ERROR-SAMPLE] {ie}")

    db.close()
    print("[SUCCESS] Diagnostics Complete")
except Exception as e:
    print(f"[ERROR] Database Issue: {e}")
