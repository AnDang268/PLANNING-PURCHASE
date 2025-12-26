from backend.database import SessionLocal
from backend.models import FactRollingInventory
from sqlalchemy import text

db = SessionLocal()
print("--- Checking FactRollingInventory Dates ---")
try:
    # Check raw SQL values (SQL Server Syntax)
    rows = db.execute(text("SELECT TOP 5 sku_id, bucket_date FROM Fact_Rolling_Inventory")).fetchall()
    for r in rows:
        print(f"Row: {r}")
        print(f"Type: {type(r[1])}")

    # Check via ORM
    rec = db.query(FactRollingInventory).first()
    if rec:
        print(f"\nORM Record: {rec.bucket_date} (Type: {type(rec.bucket_date)})")
    else:
        print("No records found.")
except Exception as e:
    print(e)
finally:
    db.close()
