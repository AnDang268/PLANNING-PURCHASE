from backend.database import engine
from sqlalchemy import text

def debug_connection():
    print("--- DIAGNOSTIC START ---")
    try:
        with engine.connect() as conn:
            # 1. Get Server and DB Name
            info = conn.execute(text("SELECT @@SERVERNAME, DB_NAME()")).fetchone()
            print(f"Connected to SQL Instance: '{info[0]}'")
            print(f"Connected to Database:     '{info[1]}'")
            
            # 2. List Tables
            print("\nListing All Tables in 'dbo' schema:")
            tables = conn.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA='dbo'")).fetchall()
            found = False
            for t in tables:
                print(f" - {t[0]}")
                if t[0] == 'Fact_Opening_Stock':
                    found = True
            
            print("--------------------------")
            if found:
                print("✅ Table 'Fact_Opening_Stock' EXISTS in this database.")
                # 3. Check columns
                cols = conn.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Fact_Opening_Stock'")).fetchall()
                print("Columns:", [c[0] for c in cols])
            else:
                print("❌ Table 'Fact_Opening_Stock' DOES NOT EXIST in this database.")

    except Exception as e:
        print(f"Connection Error: {e}")
    print("--- DIAGNOSTIC END ---")

if __name__ == "__main__":
    debug_connection()
