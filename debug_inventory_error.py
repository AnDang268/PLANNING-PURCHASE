
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import FactInventorySnapshots, DimProducts
from sqlalchemy.orm import Session
from sqlalchemy import text

def test_inventory_query():
    db = SessionLocal()
    try:
        print("Testing Inventory Query (FULL)...", flush=True)
        query = db.query(
            FactInventorySnapshots, 
            DimProducts.product_name
        ).outerjoin(DimProducts, FactInventorySnapshots.sku_id == DimProducts.sku_id)
        
        # query = db.query(FactInventorySnapshots)
        
        # Test count
        try:
            total = query.count()
            print(f"Total count: {total}", flush=True)
        except Exception as e:
            print(f"COUNT FAILED: {e}", flush=True)
            raise e

        # Test fetch
        try:
            results = query.limit(5).all()
            print(f"Fetched {len(results)} items", flush=True)
            
            data = []
            for snap, pname in results:
                # pname = "TEST"
                print(f"Processing: {snap.sku_id}", flush=True)
                item = {
                    "snapshot_date": snap.snapshot_date.isoformat() if snap.snapshot_date else None,
                    "warehouse_id": snap.warehouse_id,
                    "sku_id": snap.sku_id,
                    "product_name": pname,
                    "quantity_on_hand": snap.quantity_on_hand,
                    "quantity_on_order": snap.quantity_on_order,
                    "notes": snap.notes
                }
                data.append(item)
            print("Serialization Successful", flush=True)
            print(data, flush=True)
        except Exception as e:
            print(f"FETCH/SERIALIZE FAILED: {e}", flush=True)
            import traceback
            traceback.print_exc()
            raise e
            
        print("Query Successful", flush=True)
    except Exception as e:
        print(f"GLOBAL FAILURE: {e}", flush=True)
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_inventory_query()
