from backend.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = [c['name'] for c in inspector.get_columns('Fact_Rolling_Inventory')]
print(f"Columns in Fact_Rolling_Inventory: {columns}")

if 'warehouse_id' in columns:
    print("SUCCESS: warehouse_id exists")
else:
    print("FAILURE: warehouse_id MISSING")
