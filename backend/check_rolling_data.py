from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from backend.models import FactRollingInventory, Base
from backend.database import SQLALCHEMY_DATABASE_URL

# Setup DB
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def check_data():
    count = db.query(FactRollingInventory).count()
    print(f"Total Rows: {count}")
    
    if count > 0:
        min_date = db.query(func.min(FactRollingInventory.bucket_date)).scalar()
        max_date = db.query(func.max(FactRollingInventory.bucket_date)).scalar()
        print(f"Date Range: {min_date} to {max_date}")
        
        # Sample 5 rows
        print("Sample Data:")
        for r in db.query(FactRollingInventory).limit(5).all():
            print(f" - Date: {r.bucket_date}, SKU: {r.sku_id}, Qty: {r.opening_stock}")
    else:
        print("Table is EMPTY.")

if __name__ == "__main__":
    check_data()
