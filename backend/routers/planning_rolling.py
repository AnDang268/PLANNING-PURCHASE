
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.rolling_calc import RollingPlanningEngine
from backend.models import FactRollingInventory, DimProducts, PlanningDistributionProfile
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

router = APIRouter(
    prefix="/api/planning/rolling",
    tags=["rolling-planning"]
)

class RunCalcRequest(BaseModel):
    horizon_months: int = 12
    sku_ids: Optional[List[str]] = None
    profile_id: str = 'STD'
    group_id: Optional[str] = 'ALL'
    warehouse_id: Optional[str] = 'ALL'
    run_date: Optional[date] = None

@router.get("/products/search")
def search_products(q: str, limit: int = 20, db: Session = Depends(get_db)):
    """
    Simple search for Product Picker.
    """
    from backend.models import DimProducts
    term = f"%{q}%"
    results = db.query(DimProducts.sku_id, DimProducts.product_name)\
        .filter((DimProducts.sku_id.ilike(term)) | (DimProducts.product_name.ilike(term)))\
        .limit(limit).all()
    return [{"sku_id": r.sku_id, "product_name": r.product_name} for r in results]

@router.get("/profiles")
def get_planning_profiles(db: Session = Depends(get_db)):
    return db.query(PlanningDistributionProfile).filter_by(is_active=True).all()

@router.get("/warehouses")
def get_warehouses(db: Session = Depends(get_db)):
    from backend.models import DimWarehouses
    return db.query(DimWarehouses).all()

@router.post("/run")
def run_rolling_calculation(req: RunCalcRequest, db: Session = Depends(get_db)):
    engine = RollingPlanningEngine(db)
    try:
        engine.run_rolling_calculation(sku_list=req.sku_ids, horizon_months=req.horizon_months, profile_id=req.profile_id, group_id=req.group_id, warehouse_id=req.warehouse_id, run_date=req.run_date)
        return {"status": "success", "message": f"Calculation run with Profile {req.profile_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Helper for Recursive Groups ---
def get_recursive_group_ids(db: Session, group_id: str) -> List[str]:
    """
    Recursively fetch all child group IDs for a given group_id.
    Returns a list including the parent group_id itself.
    """
    from backend.models import DimProductGroups
    all_group_ids = [group_id]
    
    # Simple stack-based traversal to avoid deep recursion limit if hierarchy is deep
    stack = [group_id]
    visited = set([group_id])
    
    while stack:
        curr = stack.pop()
        children = db.query(DimProductGroups.group_id).filter(DimProductGroups.parent_id == curr).all()
        for c in children:
            cid = c[0]
            if cid not in visited:
                visited.add(cid)
                all_group_ids.append(cid)
                stack.append(cid)
                
    return all_group_ids

@router.get("/matrix")
def get_rolling_matrix(
    category: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    warehouse_id: Optional[str] = None,
    profile_id: str = 'STD',
    group_id: Optional[str] = None,
    search: Optional[str] = None,
    sku_ids: Optional[str] = None, # New: Comma separated list
    db: Session = Depends(get_db)
):
    # 1. Base Query for SKUs (Distinct)
    sku_query = db.query(DimProducts.sku_id)
    
    if category and category != 'ALL':
        sku_query = sku_query.filter(DimProducts.category == category)
        
    if group_id and group_id != 'ALL':
        # Recursive Filter
        target_groups = get_recursive_group_ids(db, group_id)
        sku_query = sku_query.filter((DimProducts.group_id.in_(target_groups)) | (DimProducts.category.in_(target_groups)))

    if sku_ids:
        # Filter by specific list of SKUs
        id_list = [x.strip() for x in sku_ids.split(',') if x.strip()]
        if id_list:
            sku_query = sku_query.filter(DimProducts.sku_id.in_(id_list))

    if search:
        search_term = f"%{search}%"
        # Optional: Join Group to search by group name too?
        # For now keep it simple to SKU/Name to rely on the MultiSelect for precision
        sku_query = sku_query.filter(
            (DimProducts.sku_id.ilike(search_term)) | 
            (DimProducts.product_name.ilike(search_term))
        )

    # Total Count
    total_items = sku_query.distinct().count()
    
    # 2. Paginate SKUs
    offset = (page - 1) * limit
    paged_skus_res = sku_query.distinct().order_by(DimProducts.sku_id).offset(offset).limit(limit).all()
    target_sku_ids = [s[0] for s in paged_skus_res]
    
    if not target_sku_ids:
        return {
            "data": [],
            "total": total_items,
            "page": page,
            "limit": limit,
            "total_pages": 0
        }

    # 3. Fetch Rolling Data for these SKUs
    query = db.query(
        FactRollingInventory.sku_id,
        FactRollingInventory.bucket_date,
        FactRollingInventory.opening_stock,
        FactRollingInventory.forecast_demand,
        FactRollingInventory.incoming_supply,
        FactRollingInventory.planned_supply,
        FactRollingInventory.closing_stock,
        FactRollingInventory.net_requirement,
        FactRollingInventory.min_stock_policy,
        DimProducts.product_name,
        DimProducts.category,
        DimProducts.group_id, 
        # DimProducts.group_name # If available in model
    ).join(DimProducts, FactRollingInventory.sku_id == DimProducts.sku_id)
    
    # Filter by SKUs and Profile
    query = query.filter(
        FactRollingInventory.profile_id == profile_id,
        FactRollingInventory.sku_id.in_(target_sku_ids)
    )
    
    # Optional: Warehouse Filter on Fact Table
    if warehouse_id and warehouse_id != 'ALL':
        query = query.filter(FactRollingInventory.warehouse_id == warehouse_id)

    data = query.order_by(FactRollingInventory.sku_id, FactRollingInventory.bucket_date).all()
    
    # Force Flat List Return
    result = []
    for row in data:
        result.append({
            "sku_id": row.sku_id,
            "product_name": row.product_name,
            "category": row.category,
            "bucket_date": row.bucket_date, 
            "opening_stock": row.opening_stock,
            "forecast": row.forecast_demand,
            "incoming": row.incoming_supply,
            "planned": row.planned_supply,
            "closing": row.closing_stock,
            "status": "NORMAL",
            "net_req": row.net_requirement,
            "dos": 0 # Calc if needed
        })
        
    return {
        "data": result,
        "total": total_items,
        "page": page,
        "limit": limit,
        "total_pages": (total_items + limit - 1) // limit
    }

from backend.models import PlanningPolicies

@router.get("/policies")
def get_planning_policies(db: Session = Depends(get_db)):
    """Fetch all planning policies"""
    return db.query(PlanningPolicies).all()

class UpdatePolicyRequest(BaseModel):
    safety_stock_days: int
    service_level_target: float

@router.put("/policies/{policy_id}")
def update_planning_policy(policy_id: int, req: UpdatePolicyRequest, db: Session = Depends(get_db)):
    """Update safety stock configuration"""
    policy = db.query(PlanningPolicies).filter(PlanningPolicies.policy_id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    policy.safety_stock_days = req.safety_stock_days
    policy.service_level_target = req.service_level_target
    db.commit()
    
@router.post("/import/matrix")
async def import_rolling_matrix(
    file: UploadFile = File(...),
    profile_id: str = 'STD',
    warehouse_id: str = 'ALL',
    db: Session = Depends(get_db)
):
    import pandas as pd
    import io
    from datetime import datetime
    
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # 1. Identifier Column
        sku_col = next((c for c in df.columns if str(c).lower() in ['sku', 'sku_id', 'product code']), None)
        if not sku_col:
            raise HTTPException(400, "Could not find 'SKU' column.")
            
        count = 0
        errors = []
        
        # 2. Iterate Rows
        for _, row in df.iterrows():
            sku = str(row[sku_col]).strip()
            if not sku or sku.lower() == 'nan': continue
            
            # 3. Iterate Columns for Dates
            for col in df.columns:
                col_str = str(col).strip()
                
                # Check format "YYYY-MM-DD (Planned)"
                if "(Planned)" in col_str:
                    date_part = col_str.replace("(Planned)", "").strip()
                    try:
                        bucket_date = datetime.strptime(date_part, "%Y-%m-%d").date()
                        val = row[col]
                        
                        # Update DB
                        # Note: We need to find the specific record.
                        # Ideally, we should batch these updates or use a merge statement.
                        # For MVP, row-by-row is okay for reasonable sizes (<50k cells).
                        
                        if pd.notna(val):
                            planned_qty = float(val)
                            
                            record = db.query(FactRollingInventory).filter(
                                FactRollingInventory.sku_id == sku,
                                FactRollingInventory.bucket_date == bucket_date,
                                FactRollingInventory.profile_id == profile_id,
                                FactRollingInventory.warehouse_id == warehouse_id
                            ).first()
                            
                            if record:
                                record.planned_supply = planned_qty
                                record.updated_at = datetime.now()
                                count += 1
                                
                    except ValueError:
                        continue # Not a date column
                    except Exception as e:
                        errors.append(f"SKU {sku} col {col}: {str(e)}")
                        
        db.commit()
        return {"status": "success", "message": f"Updated {count} planned supply records.", "errors": errors[:10]}
        
    except Exception as e:
        raise HTTPException(500, f"Import Failed: {str(e)}")
