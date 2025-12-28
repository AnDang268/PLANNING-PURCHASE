import sys
import os

sys.path.append(os.getcwd())
import io

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.database import SessionLocal
from backend.models import DimProducts, DimProductGroups

def check_groups():
    db = SessionLocal()
    
    sku = 'GD.UCP206.WIN'
    print(f"Checking SKU: {sku}")
    
    product = db.query(DimProducts).filter(DimProducts.sku_id == sku).first()
    
    if product:
        print(f"Found Product: {product.product_name}")
        print(f"Group ID: {product.group_id}")
        
        group = db.query(DimProductGroups).filter(DimProductGroups.group_id == product.group_id).first()
        if group:
            print(f"Group Name: {group.group_name}")
        else:
            print("Group not found in DimProductGroups")
    else:
        print("Product not found")

    # List all groups for prefixes
    print("\n--- All Groups for GD.* ---")
    prefixes = ['GD.UCF', 'GD.UCP', 'GD.UCT', 'GD.UCFL']
    group_ids = set()
    for p in prefixes:
        products = db.query(DimProducts).filter(DimProducts.sku_id.like(f"{p}%")).all()
        for prod in products:
            if prod.group_id:
                group_ids.add(prod.group_id)
    
    if group_ids:
        groups = db.query(DimProductGroups).filter(DimProductGroups.group_id.in_(list(group_ids))).all()
        for g in groups:
            print(f"ID: {g.group_id} | Name: {g.group_name}")
    else:
        print("No groups found for prefixes.")

if __name__ == "__main__":
    check_groups()
