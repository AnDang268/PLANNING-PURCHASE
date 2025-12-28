import sys
import os

sys.path.append(os.getcwd())
from backend.database import SessionLocal
from backend.models import DimProducts, DimProductGroups

def check_groups():
    db = SessionLocal()
    
    sku = 'GD.UCP206.WIN'
    output = []
    output.append(f"Checking SKU: {sku}")
    
    product = db.query(DimProducts).filter(DimProducts.sku_id == sku).first()
    
    if product:
        output.append(f"Found Product: {product.product_name}")
        output.append(f"Group ID: {product.group_id}")
        
        group = db.query(DimProductGroups).filter(DimProductGroups.group_id == product.group_id).first()
        if group:
            output.append(f"Group Name: {group.group_name}")
        else:
            output.append("Group not found in DimProductGroups")
    else:
        output.append("Product not found")

    output.append("\n--- All Groups for GD.* ---")
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
            output.append(f"ID: {g.group_id} | Name: {g.group_name}")
    else:
        output.append("No groups found for prefixes.")

    with open("group_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    check_groups()
