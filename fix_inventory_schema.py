
import sys
import os
from sqlalchemy import text

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.database import SessionLocal

def fix_schema():
    print("Connecting to DB via SessionLocal...")
    db = SessionLocal()
    try:
        # Check if column exists
        print("Checking schema for Fact_Inventory_Snapshots...")
        check_sql = "SELECT COL_LENGTH('Fact_Inventory_Snapshots', 'warehouse_id')"
        result = db.execute(text(check_sql)).scalar()
        
        if result is None:
            print("Column 'warehouse_id' is MISSING. Adding it...")
            alter_sql = "ALTER TABLE Fact_Inventory_Snapshots ADD warehouse_id NVARCHAR(50) DEFAULT 'ALL' WITH VALUES"
            db.execute(text(alter_sql))
            print("Column added successfully.")
        else:
            print("Column 'warehouse_id' already exists.")

        # Check notes
        check_notes = db.execute(text("SELECT COL_LENGTH('Fact_Inventory_Snapshots', 'notes')")).scalar()
        if check_notes is None:
            print("Column 'notes' is MISSING. Adding it...")
            db.execute(text("ALTER TABLE Fact_Inventory_Snapshots ADD notes NVARCHAR(255)"))
            print("Column 'notes' added.")

        db.commit()
        print("Schema fix applied.")
    except Exception as e:
        db.rollback()
        print(f"Error fixing schema: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    fix_schema()
