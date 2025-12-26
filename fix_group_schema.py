
from backend.database import engine
from sqlalchemy import text

def fix_schema():
    print("Fixing Schema for Dim_Customer_Groups...")
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # 1. group_name
        print("Altering group_name to NVARCHAR(255)...")
        conn.execute(text("ALTER TABLE Dim_Customer_Groups ALTER COLUMN group_name NVARCHAR(255)"))
        
        # 2. description
        print("Altering description to NVARCHAR(500)...") 
        conn.execute(text("ALTER TABLE Dim_Customer_Groups ALTER COLUMN description NVARCHAR(500)"))
        
        # 3. parent_id (Should be fine as ID, but let's check model... model says NVARCHAR(50). Let's keep it safe)
        print("Altering parent_id to NVARCHAR(50)...")
        conn.execute(text("ALTER TABLE Dim_Customer_Groups ALTER COLUMN parent_id NVARCHAR(50)"))
        
        print("Schema altered successfully.")

if __name__ == "__main__":
    fix_schema()
