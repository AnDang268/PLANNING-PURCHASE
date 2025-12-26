from backend.database import engine
from sqlalchemy import text

def check_schema():
    conn = engine.connect()
    try:
        query = text("""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME IN ('Dim_Units', 'Dim_Product_Groups') 
        AND COLUMN_NAME IN ('unit_name', 'group_name')
        """)
        
        result = conn.execute(query)
        print("--- SCHEMA CHECK ---")
        for row in result:
            print(f"Table: {row[0]}, Column: {row[1]}, Type: {row[2]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema()
