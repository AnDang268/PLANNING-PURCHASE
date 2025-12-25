
from backend.database import engine
from sqlalchemy import text

def migrate():
    print("Migrating Database Schema (Retry)...")
    # Use engine.begin() for auto-commit transaction
    with engine.begin() as conn:
        # Add abc_class
        try:
            print("Attempting to add abc_class...")
            conn.execute(text("ALTER TABLE Dim_Products ADD abc_class CHAR(1)"))
            print("SUCCESS: Added abc_class")
        except Exception as e:
            print(f"SKIPPED abc_class: {e}")

        # Add xyz_class
        try:
            print("Attempting to add xyz_class...")
            conn.execute(text("ALTER TABLE Dim_Products ADD xyz_class CHAR(1)"))
            print("SUCCESS: Added xyz_class")
        except Exception as e:
            print(f"SKIPPED xyz_class: {e}")
            
    print("Migration Script Finished.")

if __name__ == "__main__":
    migrate()
