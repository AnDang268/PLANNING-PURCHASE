from backend.database import engine
from sqlalchemy import inspect, text

inspector = inspect(engine)
columns = [c['name'] for c in inspector.get_columns('Dim_Warehouses')]
print(f"Current columns in Dim_Warehouses: {columns}")

if 'warehouse_code' in columns:
    print("VERIFIED: warehouse_code exists.")
else:
    print("MISSING: warehouse_code is NOT in the table.")
    # Try adding it again forcefully with auto-commit logic if needed, 
    # but first let's just see.
