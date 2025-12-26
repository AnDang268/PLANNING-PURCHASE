
from sqlalchemy import create_engine, text
from backend.database import DATABASE_URL

def add_columns():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            print("Adding actual_sold_qty...")
            conn.execute(text("ALTER TABLE Fact_Rolling_Inventory ADD actual_sold_qty FLOAT DEFAULT 0"))
            print("Added actual_sold_qty.")
        except Exception as e:
            print(f"Error adding actual_sold_qty (might exist): {e}")

        try:
            print("Adding actual_imported_qty...")
            conn.execute(text("ALTER TABLE Fact_Rolling_Inventory ADD actual_imported_qty FLOAT DEFAULT 0"))
            print("Added actual_imported_qty.")
        except Exception as e:
            print(f"Error adding actual_imported_qty (might exist): {e}")
            
        conn.commit()
    print("Migration Check Complete.")

if __name__ == "__main__":
    add_columns()
