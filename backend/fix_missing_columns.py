from backend.database import engine
from sqlalchemy import text

def fix_columns():
    print("Fixing missing columns in Fact_Rolling_Inventory...")
    
    sqls = [
        # Add actual_sold_qty
        "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[Fact_Rolling_Inventory]') AND name = 'actual_sold_qty') ALTER TABLE Fact_Rolling_Inventory ADD actual_sold_qty FLOAT DEFAULT 0",
        
        # Add actual_imported_qty
        "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[Fact_Rolling_Inventory]') AND name = 'actual_imported_qty') ALTER TABLE Fact_Rolling_Inventory ADD actual_imported_qty FLOAT DEFAULT 0",
        
        # Add is_manual_opening
        "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[Fact_Rolling_Inventory]') AND name = 'is_manual_opening') ALTER TABLE Fact_Rolling_Inventory ADD is_manual_opening BIT DEFAULT 0"
    ]
    
    try:
        with engine.connect() as conn:
            for sql in sqls:
                try:
                    conn.execute(text(sql))
                    print(f"Executed: {sql}")
                except Exception as e:
                    print(f"Error executing sql: {e}")
            conn.commit()
            print("Migration Completed.")
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    fix_columns()
