import sys
import os
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine

def fix_relations():
    print(">>> Applying Database Constraints (Foreign Keys)...")
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # 0. ALIGN DATA TYPES (Fix NVARCHAR vs VARCHAR mismatch)
            print("   > Aligning Column Types...")
            # Products
            conn.execute(text("ALTER TABLE Dim_Products ALTER COLUMN group_id VARCHAR(50)"))
            conn.execute(text("ALTER TABLE Dim_Products ALTER COLUMN base_unit_id VARCHAR(50)"))
            # Customers
            conn.execute(text("ALTER TABLE Dim_Customers ALTER COLUMN group_id VARCHAR(50)"))
            # Vendors
            conn.execute(text("ALTER TABLE Dim_Vendors ALTER COLUMN group_id VARCHAR(50)"))

            # 1. Dim_Products -> Dim_Product_Groups
            print("   > Applying FK: Dim_Products.group_id -> Dim_Product_Groups.group_id")
            # First, handle orphans: Set invalid group_ids to NULL
            conn.execute(text("""
                UPDATE Dim_Products 
                SET group_id = NULL 
                WHERE group_id IS NOT NULL 
                AND group_id NOT IN (SELECT group_id FROM Dim_Product_Groups)
            """))
            
            # Check if FK exists before adding
            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE object_id = OBJECT_ID(N'FK_Products_Groups') AND parent_object_id = OBJECT_ID(N'Dim_Products'))
                ALTER TABLE Dim_Products 
                ADD CONSTRAINT FK_Products_Groups FOREIGN KEY (group_id) REFERENCES Dim_Product_Groups(group_id);
            """))

            # 2. Dim_Products -> Dim_Units
            print("   > Applying FK: Dim_Products.base_unit_id -> Dim_Units.unit_id")
            # Handle orphans
            conn.execute(text("""
                UPDATE Dim_Products 
                SET base_unit_id = NULL 
                WHERE base_unit_id IS NOT NULL 
                AND base_unit_id NOT IN (SELECT unit_id FROM Dim_Units)
            """))
            
            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE object_id = OBJECT_ID(N'FK_Products_Units') AND parent_object_id = OBJECT_ID(N'Dim_Products'))
                ALTER TABLE Dim_Products 
                ADD CONSTRAINT FK_Products_Units FOREIGN KEY (base_unit_id) REFERENCES Dim_Units(unit_id);
            """))

            # 3. Dim_Customers -> Dim_Customer_Groups
            print("   > Applying FK: Dim_Customers.group_id -> Dim_Customer_Groups.group_id")
            # Handle orphans
            conn.execute(text("""
                UPDATE Dim_Customers
                SET group_id = NULL 
                WHERE group_id IS NOT NULL 
                AND group_id NOT IN (SELECT group_id FROM Dim_Customer_Groups)
            """))
            
            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE object_id = OBJECT_ID(N'FK_Customers_Groups') AND parent_object_id = OBJECT_ID(N'Dim_Customers'))
                ALTER TABLE Dim_Customers 
                ADD CONSTRAINT FK_Customers_Groups FOREIGN KEY (group_id) REFERENCES Dim_Customer_Groups(group_id);
            """))

            # 4. Dim_Vendors -> Dim_Customer_Groups (Shared Dictionary)
            print("   > Applying FK: Dim_Vendors.group_id -> Dim_Customer_Groups.group_id")
            # Handle orphans
            conn.execute(text("""
                UPDATE Dim_Vendors
                SET group_id = NULL 
                WHERE group_id IS NOT NULL 
                AND group_id NOT IN (SELECT group_id FROM Dim_Customer_Groups)
            """))

            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE object_id = OBJECT_ID(N'FK_Vendors_Groups') AND parent_object_id = OBJECT_ID(N'Dim_Vendors'))
                ALTER TABLE Dim_Vendors 
                ADD CONSTRAINT FK_Vendors_Groups FOREIGN KEY (group_id) REFERENCES Dim_Customer_Groups(group_id);
            """))

            trans.commit()
            print(">>> SUCCESS: All relationships enforced successfully.")
            
        except Exception as e:
            trans.rollback()
            print(f">>> ERROR: Failed to apply constraints. {e}")

if __name__ == "__main__":
    fix_relations()
