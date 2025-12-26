
import sys
import os
# Ensure we are in root
os.chdir(r"d:\Document\SOURCE\PLANNING-PURCHASE")
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, text
from backend.database import DATABASE_URL

def add_columns():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            print("Adding extra_data to Fact_Sales...")
            conn.execute(text("ALTER TABLE Fact_Sales ADD extra_data NVARCHAR(MAX)")) 
            print("Added extra_data.")
        except Exception as e:
            print(f"Error adding extra_data (might exist): {e}")
            
        conn.commit()
    print("Migration Check Complete.")

if __name__ == "__main__":
    add_columns()
