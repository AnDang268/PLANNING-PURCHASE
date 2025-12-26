
import sys
import os
from sqlalchemy import text, desc
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import FactPurchasePlans, DimProducts

def debug_plans():
    db = SessionLocal()
    try:
        # Create a dummy plan if none exist
        if db.query(FactPurchasePlans).count() == 0:
            print("No plans found. Creating dummy plan for testing...")
            # Ensure SKU exists
            sku = db.query(DimProducts).first()
            if not sku:
                sku = DimProducts(sku_id="TEST-SKU", product_name="Test Product")
                db.add(sku)
                db.commit()
            
            plan = FactPurchasePlans(
                plan_date=datetime.now(),
                sku_id=sku.sku_id,
                suggested_quantity=10,
                final_quantity=10,
                status="PENDING"
            )
            db.add(plan)
            db.commit()
        
        print("Querying FactPurchasePlans...")
        query = db.query(FactPurchasePlans).join(DimProducts, FactPurchasePlans.sku_id == DimProducts.sku_id)
        
        plans = query.order_by(desc(FactPurchasePlans.created_at)).limit(10).all()
        
        results = []
        for p in plans:
            print(f"Processing Plan {p.plan_id}...")
            item = {
                "id": p.plan_id,
                "plan_date": p.plan_date.strftime("%Y-%m-%d") if p.plan_date else None, # Potential error point
                "sku_id": p.sku_id,
                "vendor_id": p.vendor_id,
                "suggested_quantity": p.suggested_quantity,
                "final_quantity": p.final_quantity,
                "total_amount": p.total_amount,
                "status": p.status,
                "notes": p.notes
            }
            results.append(item)
            
        print("Serialization Successful.")
        print(results)
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_plans()
