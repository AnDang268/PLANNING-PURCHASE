from backend.database import engine
from sqlalchemy import text

def upgrade_schema():
    with engine.connect() as conn:
        print("Checking and Upgrading Schema...")
        
        # 1. Dim_Customers
        try:
            print("Altering Dim_Customers.phone -> NVARCHAR(100)...")
            conn.execute(text("ALTER TABLE Dim_Customers ALTER COLUMN phone NVARCHAR(100)"))
            print("Altering Dim_Customers.misa_code -> NVARCHAR(100)...")
            conn.execute(text("ALTER TABLE Dim_Customers ALTER COLUMN misa_code NVARCHAR(100)"))
            print("Altering Dim_Customers.email -> NVARCHAR(255)...")
            conn.execute(text("ALTER TABLE Dim_Customers ALTER COLUMN email NVARCHAR(255)"))
        except Exception as e:
            print(f"Dim_Customers Error (might already exist): {e}")

        # 2. Dim_Vendors
        try:
            print("Altering Dim_Vendors.phone -> NVARCHAR(100)...")
            conn.execute(text("ALTER TABLE Dim_Vendors ALTER COLUMN phone NVARCHAR(100)"))
            print("Altering Dim_Vendors.email -> NVARCHAR(255)...")
            conn.execute(text("ALTER TABLE Dim_Vendors ALTER COLUMN email NVARCHAR(255)"))
        except Exception as e:
             print(f"Dim_Vendors Error: {e}")

        conn.commit()
        print("Schema Upgrade Completed.")

if __name__ == "__main__":
    upgrade_schema()
