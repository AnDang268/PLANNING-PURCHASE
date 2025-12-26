from backend.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = inspector.get_columns('Dim_Product_Groups')
print("Columns in Dim_Product_Groups:")
for c in columns:
    print(f"- {c['name']} ({c['type']})")

columns_prod = inspector.get_columns('Dim_Products')
print("\nColumns in Dim_Products:")
for c in columns_prod:
    print(f"- {c['name']} ({c['type']})")
