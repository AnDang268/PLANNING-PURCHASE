from backend.database import SessionLocal, engine
from sqlalchemy import text

def reset_transactions():
    """
    Clears all Transaction (Fact) tables to provide a clean slate.
    Preserves Master Data (Dim) tables.
    """
    tables_to_clear = [
        "Fact_Rolling_Inventory",
        "Fact_Purchase_Plans",
        "Fact_Opening_Stock",
        "Fact_Inventory_Snapshots",
        "Fact_Sales",
        "Fact_Purchases",
        "Fact_Forecasts",
        "System_Sync_Logs" 
    ]
    
    confirm = input(f"WARING: This will DELETE ALL DATA from {len(tables_to_clear)} transaction tables. Are you sure? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            print("Starting Data Reset...")
            for tbl in tables_to_clear:
                print(f"  Clearing {tbl}...")
                conn.execute(text(f"DELETE FROM {tbl}"))
                
            trans.commit()
            print("✔ Reset Complete. All transaction data cleared.")
            print("You can now re-import your files to get a 100% clean state.")
        except Exception as e:
            trans.rollback()
            print(f"❌ Reset Failed: {e}")

if __name__ == "__main__":
    reset_transactions()
