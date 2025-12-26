from backend.database import engine
from sqlalchemy import text

def add_column():
    with engine.connect() as conn:
        try:
            # Check if column exists first (SQL Server specific info schema check, or just try catch)
            # Simple approach: Try to add, if fails assumes exists (or catch specific error)
            # Better: Check schema.
            
            check_sql = """
            SELECT COL_LENGTH('Dim_Products', 'distribution_profile_id')
            """
            result = conn.execute(text(check_sql)).scalar()
            
            if result is not None:
                print("Column 'distribution_profile_id' already exists in 'Dim_Products'.")
            else:
                print("Adding column 'distribution_profile_id' to 'Dim_Products'...")
                alter_sql = """
                ALTER TABLE Dim_Products
                ADD distribution_profile_id NVARCHAR(50) NULL;
                """
                conn.execute(text(alter_sql))
                conn.commit()
                print("Column added successfully.")
                
            # Also add FK constraint if possible, but optional for MVP as app logic handles it.
            # Adding FK ensures integrity.
            # We need to know the name of the Profile table: Planning_Distribution_Profiles
            
            # Check Constraint
            # ... skip for now to avoid complexity with naming constraints.
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    add_column()
