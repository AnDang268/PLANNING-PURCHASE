from backend.database import engine
from sqlalchemy import inspect
import json

inspector = inspect(engine)
tables = inspector.get_table_names()

print(f"--- DATABASE SCHEMA AUDIT ---")
print(f"Existing Tables: {tables}")

TARGET_TABLES = [
    "Dim_Products", 
    "Dim_Customers", 
    "Dim_Vendors", 
    "Dim_Units", 
    "Dim_Product_Groups",
    "Dim_Customer_Groups",
    "Dim_Warehouses"
]

for t in TARGET_TABLES:
    if t in tables:
        print(f"\n[TABLE] {t}")
        columns = inspector.get_columns(t)
        for c in columns:
            print(f"  - {c['name']} ({c['type']})")
    else:
        print(f"\n[MISSING] {t}")
