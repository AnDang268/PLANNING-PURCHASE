
from backend.database import engine
from sqlalchemy import inspect

def check_schema():
    inspector = inspect(engine)
    columns = inspector.get_columns('Dim_Customer_Groups')
    print("--- Dim_Customer_Groups Schema ---")
    for c in columns:
        print(f"{c['name']}: {c['type']}")

    columns_cust = inspector.get_columns('Dim_Customers')
    print("\n--- Dim_Customers Schema ---")
    for c in columns_cust:
        print(f"{c['name']}: {c['type']}")

if __name__ == "__main__":
    check_schema()
