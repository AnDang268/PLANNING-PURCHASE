
from backend.database import engine
from sqlalchemy import text

def debug_schema_rolling():
    print("Checking Schema for Dim_Products...")
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Dim_Products'"))
            columns = [row[0] for row in result]
            for c in columns: print(f"- {c}")
            
            if not columns:
                print("TABLE DOES NOT EXIST!")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_schema_rolling()
