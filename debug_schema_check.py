import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine
from sqlalchemy import inspect

def check_schema():
    inspector = inspect(engine)
    
    tables = ['Dim_Products', 'Dim_Product_Groups', 'Dim_Units', 'Dim_Customers', 'Dim_Vendors']
    
    print("\n--- DATABASE SCHEMA INSPECTION ---\n")
    
    for table in tables:
        if inspector.has_table(table):
            print(f"Table: {table}")
            columns = inspector.get_columns(table)
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")
        else:
            print(f"Table: {table} DOES NOT EXIST")
        print("-" * 30)

if __name__ == "__main__":
    check_schema()
