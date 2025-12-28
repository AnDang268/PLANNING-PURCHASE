import sys
import os

# Add root to sys.path
sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import DimProducts, DimProductGroups

def check_groups():
    db = SessionLocal()
    
    # Representative SKUs from the user's image
    target_prefixes = ['GD.UCF', 'GD.UCFL', 'GD.UCP', 'GD.UCT']
    
    print(f"{'PREFIX':<10} | {'GROUP ID':<15} | {'GROUP NAME'}")
    print("-" * 50)
    
    for prefix in target_prefixes:
        # distinct groups for this prefix
        results = db.query(DimProductGroups.group_id, DimProductGroups.group_name)\
            .join(DimProducts, DimProducts.group_id == DimProductGroups.group_id)\
            .filter(DimProducts.sku_id.like(f"{prefix}%"))\
            .distinct().all()
            
        for r in results:
            print(f"{prefix:<10} | {r.group_id:<15} | {r.group_name}")

if __name__ == "__main__":
    check_groups()
