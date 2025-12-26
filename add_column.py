from backend.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("Adding warehouse_id column...")
    try:
        conn.execute(text("ALTER TABLE Fact_Rolling_Inventory ADD warehouse_id NVARCHAR(50) DEFAULT 'ALL'"))
        conn.commit()
        print("SUCCESS: Column added.")
    except Exception as e:
        print(f"ERROR (might already exist?): {e}")
