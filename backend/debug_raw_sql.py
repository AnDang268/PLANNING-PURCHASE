
from backend.database import engine
from sqlalchemy import text

def debug_raw():
    print("Testing Columns Raw SQL...")
    columns = [
        "sku_id", "product_name", "category", "unit", 
        "min_stock_level", "max_stock_level", "moq", "pack_size",
        "supplier_lead_time_days", "policy_id", 
        "abc_class", "xyz_class", 
        "created_at", "updated_at"
    ]
    
    with engine.connect() as conn:
        for col in columns:
            try:
                print(f"Testing [{col}]...", end=" ")
                conn.execute(text(f"SELECT TOP 1 {col} FROM Dim_Products"))
                print("OK")
            except Exception as e:
                print("FAIL!")
                print(e)
                break

if __name__ == "__main__":
    debug_raw()
