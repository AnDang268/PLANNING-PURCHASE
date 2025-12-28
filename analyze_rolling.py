from datetime import date
from sqlalchemy import func
import sys
import os

# Add parent directory to path
sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import FactRollingInventory

def analyze_rolling_data():
    db = SessionLocal()
    
    print("--- Fact_Rolling_Inventory Analysis ---")
    
    # Check Profiles
    profiles = db.query(
        FactRollingInventory.profile_id, 
        func.count(FactRollingInventory.sku_id)
    ).group_by(FactRollingInventory.profile_id).all()
    
    print("\nProfiles Found:")
    for p, count in profiles:
        print(f"  - Profile: '{p}' | Count: {count}")
        
    # Check Warehouses
    warehouses = db.query(
        FactRollingInventory.warehouse_id, 
        func.count(FactRollingInventory.sku_id)
    ).group_by(FactRollingInventory.warehouse_id).all()
    
    print("\nWarehouses Found:")
    for w, count in warehouses:
        print(f"  - Warehouse: '{w}' | Count: {count}")

    # Check for same SKU/Date duplication across profiles
    # Pick a random SKU
    sku = db.query(FactRollingInventory.sku_id).first()
    if sku:
        sku = sku[0]
        print(f"\nChecking SKU: {sku}")
        rows = db.query(
            FactRollingInventory.bucket_date, 
            FactRollingInventory.profile_id, 
            FactRollingInventory.warehouse_id
        ).filter(FactRollingInventory.sku_id == sku).order_by(FactRollingInventory.bucket_date).limit(10).all()
        
        for r in rows:
            print(f"  Date: {r.bucket_date} | Profile: {r.profile_id} | Warehouse: {r.warehouse_id}")

    db.close()

if __name__ == "__main__":
    analyze_rolling_data()
