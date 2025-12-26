from backend.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("Adding warehouse_code column to Dim_Warehouses...")
    try:
        conn.execute(text("ALTER TABLE Dim_Warehouses ADD warehouse_code NVARCHAR(50)"))
        conn.commit()
        print("SUCCESS: Column 'warehouse_code' added.")
    except Exception as e:
        print(f"ERROR (might already exist?): {e}")
