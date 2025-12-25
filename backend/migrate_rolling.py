
from backend.database import engine, Base
from backend.models import FactRollingInventory

def migrate_rolling():
    print("Migrating Rolling Inventory Table...")
    # Use SQLAlchemy to create table if not exists
    Base.metadata.create_all(bind=engine)
    print("Migration Complete: Fact_Rolling_Inventory created.")

if __name__ == "__main__":
    migrate_rolling()
