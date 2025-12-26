
from backend.database import SessionLocal
from sqlalchemy import text

def add_columns():
    db = SessionLocal()
    try:
        print("Checking/Adding quantity_allocated column...")
        try:
            # Check if column exists
            db.execute(text("SELECT quantity_allocated FROM Fact_Inventory_Snapshots TOP 1"))
            print("Column quantity_allocated already exists.")
        except Exception:
            # Add column if not exists
            print("Adding quantity_allocated column...")
            db.execute(text("ALTER TABLE Fact_Inventory_Snapshots ADD quantity_allocated FLOAT DEFAULT 0"))
            db.commit()
            print("Column added successfully.")
            
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_columns()
