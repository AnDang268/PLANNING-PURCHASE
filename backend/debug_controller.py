
from backend.database import SessionLocal, engine
from backend.models import DimProducts
from sqlalchemy import text

def debug_direct_query():
    print("Direct Logic Debugging...")
    db = SessionLocal()
    try:
        # Simulate exactly what the API does
        print("Executing Query: db.query(DimProducts).order_by(DimProducts.sku_id).offset(0).limit(20).all()")
        products = db.query(DimProducts).order_by(DimProducts.sku_id).offset(0).limit(20).all()
        print(f"SUCCESS. Found {len(products)} products.")
        for p in products:
            print(f" - {p.sku_id}: {p.product_name}")
            
    except Exception as e:
        print("\n!!! EXCEPTION CAUGHT !!!")
        print(e)
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_direct_query()
