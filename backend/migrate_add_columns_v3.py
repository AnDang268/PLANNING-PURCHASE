
from backend.database import engine
from sqlalchemy import text

def migrate():
    print("Migrating Database Schema (Final)...")
    with engine.begin() as conn:
        # Add max_stock_level
        try:
            print("Attempting to add max_stock_level...")
            conn.execute(text("ALTER TABLE Dim_Products ADD max_stock_level FLOAT DEFAULT 0"))
            print("SUCCESS: Added max_stock_level")
        except Exception as e:
            print(f"SKIPPED max_stock_level: {e}")

        # Add policy_id
        try:
            print("Attempting to add policy_id...")
            conn.execute(text("ALTER TABLE Dim_Products ADD policy_id INT NULL"))
            print("SUCCESS: Added policy_id")
        except Exception as e:
            print(f"SKIPPED policy_id: {e}")
            
    print("Migration Script Finished.")

if __name__ == "__main__":
    migrate()
