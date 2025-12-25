
from backend.database import SessionLocal
from backend.models import DimProducts, FactSales
from datetime import datetime, timedelta
import random

def seed_data():
    db = SessionLocal()
    print("Seeding Data...")
    
    # 1. Create Products
    products = [
        {"sku": "IPHONE-15", "name": "iPhone 15 Pro", "cat": "Electronics", "price": 25000000},
        {"sku": "LGM-WASH", "name": "LG Washing Machine", "cat": "Appliances", "price": 8000000},
        {"sku": "SNY-TV-55", "name": "Sony Bravia 55", "cat": "Electronics", "price": 12000000},
    ]
    
    for p in products:
        existing = db.query(DimProducts).filter(DimProducts.sku_id == p['sku']).first()
        if not existing:
            db.add(DimProducts(
                sku_id=p['sku'],
                product_name=p['name'],
                category=p['cat'],
                unit="Unit",
                min_stock_level=10,
                max_stock_level=100
            ))
            print(f"Added Product: {p['sku']}")
            
    db.commit()

    # 2. Create Sales History (Last 90 Days)
    # Simple Pattern: Base demand + Random noise + Trend
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    total_sales = 0
    for p in products:
        current = start_date
        while current <= end_date:
            # Check if exists
            exists = db.query(FactSales).filter(
                FactSales.sku_id == p['sku'],
                FactSales.order_date == current
            ).first()
            
            if not exists:
                qty = max(0, int(random.gauss(20, 5))) # Mean 20, Std 5
                if current.weekday() >= 5: # Weekend spike
                    qty += 5
                
                db.add(FactSales(
                    transaction_id=f"TXN-{p['sku']}-{current.strftime('%Y%m%d')}",
                    order_id=f"ORD-{current.strftime('%Y%m%d')}",
                    sku_id=p['sku'],
                    order_date=current,
                    quantity=qty,
                    amount=qty * p['price'],
                    customer_id="CUST-DEMO"
                ))
                total_sales += 1
            current += timedelta(days=1)
            
    db.commit()
    print(f"Seeding Complete. Added {total_sales} sales records.")
    db.close()

if __name__ == "__main__":
    seed_data()
