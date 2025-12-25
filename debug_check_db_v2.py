from backend.database import SessionLocal
from sqlalchemy import text

print("--- DIAGNOSTIC DB CHECK V2 ---")
db = SessionLocal()
try:
    # 1. Simple Connection Check
    db.execute(text("SELECT 1"))
    print("[OK] Database Connection")

    # 2. Count Records (Using Correct Table Names)
    prod_count = db.execute(text("SELECT COUNT(*) FROM Dim_Products")).scalar()
    order_count = db.execute(text("SELECT COUNT(*) FROM Fact_Sales")).scalar()
    
    print(f"[DATA] Products: {prod_count}")
    print(f"[DATA] Orders:   {order_count}")

    # 3. Sample Data
    if prod_count > 0:
        print("\n--- SAMPLE REAL DATA (PROOF) ---")
        samples = db.execute(text("SELECT TOP 5 sku_id, product_name FROM Dim_Products")).fetchall()
        for s in samples:
            print(f"SKU: {s[0]} | Name: {s[1]}")
    else:
        print("[WARNING] Products table is EMPTY!")

    db.close()
    print("[SUCCESS] Diagnostics Complete")

except Exception as e:
    print(f"[ERROR] {e}")
