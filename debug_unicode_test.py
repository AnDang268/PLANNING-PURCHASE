import sys
import os
from sqlalchemy import text
from datetime import datetime

# Add parent directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine, get_db
from backend.models import DimProducts

def test_unicode_insert():
    print(">>> Testing Unicode Insertion...")
    
    # Test Data
    test_sku = "TEST-UNICODE-001"
    test_name = "Áo Thun Cổ Tròn Chất Lượng Cao" # Vietnamese Chars
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # 1. Cleanup
            conn.execute(text(f"DELETE FROM Dim_Products WHERE sku_id = '{test_sku}'"))
            
            # 2. Insert via ORM (Simulated)
            print(f"   > Inserting: {test_name}")
            
            # Use raw SQL first to test driver
            # N prefix is critical in raw SQL, but ORM should handle it.
            # Let's test ORM behavior since that's what app uses.
            pass
            trans.commit()
        except:
            trans.rollback()
            raise

    # ORM Insert
    db = next(get_db())
    try:
        product = DimProducts(
            sku_id=test_sku,
            product_name=test_name,
            min_stock_level=10
        )
        db.add(product)
        db.commit()
        print("   > Insert Committed.")
        
        # 3. Read Back
        obj = db.query(DimProducts).filter(DimProducts.sku_id == test_sku).first()
        print(f"   > Read Back: {obj.product_name}")
        
        if obj.product_name == test_name:
            print(">>> SUCCESS: Unicode preserved correctly.")
        else:
            print(f">>> FAILURE: Unicode mismatch. Got: {obj.product_name}")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_unicode_insert()
