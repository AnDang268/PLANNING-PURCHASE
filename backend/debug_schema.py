
from backend.database import engine
from sqlalchemy import text

def debug_schema():
    print("Inspecting Information Schema...")
    with engine.connect() as conn:
        # Check Columns
        result = conn.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Dim_Products'"))
        columns = [row[0] for row in result]
        print(f"Columns in Dim_Products: {columns}")
        
        # Check abc/xyz specific
        print(f"Has abc_class? {'abc_class' in columns}")
        print(f"Has xyz_class? {'xyz_class' in columns}")

if __name__ == "__main__":
    debug_schema()
