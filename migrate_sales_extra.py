
import sys
import os
from sqlalchemy import create_engine, text

# Fix path
sys.path.append(os.getcwd())

from backend.database import DATABASE_URL

def add_columns():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            print("Adding extra_data to Fact_Sales...")
            conn.execute(text("ALTER TABLE Fact_Sales ADD extra_data NVARCHAR(MAX)")) # SQL Server Syntax
            print("Added extra_data.")
        except Exception as e:
            print(f"Error adding extra_data (might exist): {e}")
            
        conn.commit()
    print("Migration Check Complete.")

if __name__ == "__main__":
    add_columns()
