from backend.database import engine
from sqlalchemy import text

def fix_schema():
    conn = engine.connect()
    try:
        commands = [
            # Dim_Units
            "ALTER TABLE Dim_Units ALTER COLUMN unit_name NVARCHAR(100)",
            "ALTER TABLE Dim_Units ALTER COLUMN description NVARCHAR(255)",
            
            # Dim_Product_Groups
            "ALTER TABLE Dim_Product_Groups ALTER COLUMN group_name NVARCHAR(255)",
            
            # Dim_Products
            "ALTER TABLE Dim_Products ALTER COLUMN product_name NVARCHAR(255)",
            "ALTER TABLE Dim_Products ALTER COLUMN category NVARCHAR(100)",
            "ALTER TABLE Dim_Products ALTER COLUMN unit NVARCHAR(50)",
            
            # Dim_Vendors
            "ALTER TABLE Dim_Vendors ALTER COLUMN vendor_name NVARCHAR(255)",
            "ALTER TABLE Dim_Vendors ALTER COLUMN contact_person NVARCHAR(100)",
            "ALTER TABLE Dim_Vendors ALTER COLUMN address NVARCHAR(500)",
            
            # Dim_Customers
            "ALTER TABLE Dim_Customers ALTER COLUMN customer_name NVARCHAR(255)",
            "ALTER TABLE Dim_Customers ALTER COLUMN address NVARCHAR(500)",

            # Dim_Warehouses
            "ALTER TABLE Dim_Warehouses ALTER COLUMN warehouse_name NVARCHAR(255)",
            "ALTER TABLE Dim_Warehouses ALTER COLUMN address NVARCHAR(500)",
        ]
        
        print("--- STARTING SCHEMA UPDATE (VARCHAR -> NVARCHAR) ---")
        trans = conn.begin()
        for cmd in commands:
            print(f"Executing: {cmd}")
            conn.execute(text(cmd))
        
        trans.commit()
        print("--- SCHEMA UPDATE COMPLETED SUCCESSFULLY ---")
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()
