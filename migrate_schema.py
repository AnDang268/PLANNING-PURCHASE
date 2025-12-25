from backend.database import engine, Base
from sqlalchemy import text

print("--- MIGRATING SCHEMA ---")

# 1. Create New Tables (Dim_Units, Dim_Product_Groups, Dim_Customer_Groups)
Base.metadata.create_all(bind=engine)
print("[OK] Created missing tables (Dim_Units, Dim_Product_Groups, Dim_Customer_Groups)")

# 2. Alter Existing Tables
alter_commands = [
    # Dim_Products
    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'Dim_Products') AND name = 'group_id') ALTER TABLE Dim_Products ADD group_id NVARCHAR(50);",
    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'Dim_Products') AND name = 'base_unit_id') ALTER TABLE Dim_Products ADD base_unit_id NVARCHAR(50);",
    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'Dim_Products') AND name = 'amis_act_id') ALTER TABLE Dim_Products ADD amis_act_id NVARCHAR(50);",
    
    # Dim_Customers
    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'Dim_Customers') AND name = 'group_id') ALTER TABLE Dim_Customers ADD group_id NVARCHAR(50);",
    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'Dim_Customers') AND name = 'misa_code') ALTER TABLE Dim_Customers ADD misa_code NVARCHAR(50);",
    
    # Dim_Vendors
    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'Dim_Vendors') AND name = 'email') ALTER TABLE Dim_Vendors ADD email NVARCHAR(100);",
    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'Dim_Vendors') AND name = 'tax_code') ALTER TABLE Dim_Vendors ADD tax_code NVARCHAR(50);",
    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'Dim_Vendors') AND name = 'group_id') ALTER TABLE Dim_Vendors ADD group_id NVARCHAR(50);",
    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'Dim_Vendors') AND name = 'address') ALTER TABLE Dim_Vendors ADD address NVARCHAR(500);"
]

with engine.connect() as conn:
    for cmd in alter_commands:
        try:
            conn.execute(text(cmd))
            print(f"[OK] Executed: {cmd[:80]}...")
        except Exception as e:
            print(f"[WARN] Failed: {e}")
    conn.commit()

print("[SUCCESS] Schema Migration Finished.")
