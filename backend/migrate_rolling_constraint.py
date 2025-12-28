from backend.database import SessionLocal, engine
from sqlalchemy import text

def migrate_rolling_constraint():
    with engine.connect() as conn:
        try:
            print("Checking for existing constraint 'uq_rolling_inventory'...")
            # SQL Server check for constraint
            chk = conn.execute(text("SELECT name FROM sys.key_constraints WHERE name = 'uq_rolling_inventory'")).scalar()
            if not chk:
                print("Adding UniqueConstraint 'uq_rolling_inventory' to Fact_Rolling_Inventory...")
                # Note: This might fail if duplicates exist (but we checked and found 0)
                conn.execute(text("ALTER TABLE Fact_Rolling_Inventory ADD CONSTRAINT uq_rolling_inventory UNIQUE (sku_id, warehouse_id, bucket_date, profile_id)"))
                conn.commit()
                print("Constraint Added Successfully.")
            else:
                print("Constraint 'uq_rolling_inventory' already exists.")
        except Exception as e:
            print(f"Migration Failed: {e}")

if __name__ == "__main__":
    migrate_rolling_constraint()
