
from backend.database import engine
from sqlalchemy import text

def migrate():
    print("Migrating Database Schema...")
    with engine.connect() as conn:
        # Add abc_class
        try:
            conn.execute(text("ALTER TABLE Dim_Products ADD abc_class CHAR(1)"))
            print("Added abc_class to Dim_Products")
        except Exception as e:
            print(f"abc_class might already exist: {e}")

        # Add xyz_class
        try:
            conn.execute(text("ALTER TABLE Dim_Products ADD xyz_class CHAR(1)"))
            print("Added xyz_class to Dim_Products")
        except Exception as e:
            print(f"xyz_class might already exist: {e}")
            
        conn.commit()
    print("Migration Complete.")

if __name__ == "__main__":
    migrate()
