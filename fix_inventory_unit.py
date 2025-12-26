
from backend.database import SessionLocal
from sqlalchemy import text

def add_unit_column():
    db = SessionLocal()
    try:
        print("Checking/Adding unit column...")
        try:
            db.execute(text("SELECT unit FROM Fact_Inventory_Snapshots TOP 1"))
            print("Column unit already exists.")
        except Exception:
            print("Adding unit column...")
            db.execute(text("ALTER TABLE Fact_Inventory_Snapshots ADD unit NVARCHAR(50)"))
            db.commit()
            print("Column added successfully.")
            
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_unit_column()
