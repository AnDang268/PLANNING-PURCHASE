from sqlalchemy import text
from backend.database import SessionLocal, engine

def run_migration():
    print("Migrating: Adding warehouse_id to Fact_Sales and Fact_Purchases...")
    
    with engine.connect() as conn:
        # 1. Fact_Sales
        try:
            conn.execute(text("SELECT warehouse_id FROM Fact_Sales TOP 1"))
            print("Fact_Sales already has warehouse_id.")
        except:
            print("Adding warehouse_id to Fact_Sales...")
            conn.execute(text("ALTER TABLE Fact_Sales ADD warehouse_id NVARCHAR(255) DEFAULT '66 An dương vương' WITH VALUES"))
            conn.commit()

        # 2. Fact_Purchases
        try:
            conn.execute(text("SELECT warehouse_id FROM Fact_Purchases TOP 1"))
            print("Fact_Purchases already has warehouse_id.")
        except:
            print("Adding warehouse_id to Fact_Purchases...")
            conn.execute(text("ALTER TABLE Fact_Purchases ADD warehouse_id NVARCHAR(255) DEFAULT '66 An dương vương' WITH VALUES"))
            conn.commit()

    print("Migration Complete.")

if __name__ == "__main__":
    run_migration()
