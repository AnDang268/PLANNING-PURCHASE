
from fastapi import APIRouter, Depends, HTTPException, Query
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

@router.get("/profiles")
def get_planning_profiles(db: Session = Depends(get_db)):
    return db.query(PlanningDistributionProfile).filter_by(is_active=True).all()

@router.post("/run")
def run_rolling_calculation(req: RunCalcRequest, db: Session = Depends(get_db)):
    engine = RollingPlanningEngine(db)
    try:
        engine.run_rolling_calculation(sku_list=req.sku_ids, horizon_months=req.horizon_months, profile_id=req.profile_id)
        return {"status": "success", "message": f"Calculation run with Profile {req.profile_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/matrix")
def get_rolling_matrix(
    category: Optional[str] = None,
    limit: int = 5000,
    warehouse_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Retrieve specific columns to avoid implicit join issues and improve performance
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
        # FactRollingInventory.status, # Field might not exist in Model? Check model definition. It's often dynamic property.
        DimProducts.product_name,
        DimProducts.category
    ).join(DimProducts, FactRollingInventory.sku_id == DimProducts.sku_id)
        
    if category and category != 'ALL':
        query = query.filter(DimProducts.category == category)
        
    data = query.order_by(FactRollingInventory.sku_id, FactRollingInventory.bucket_date).limit(limit).all()
    
    result = []
    for row in data:
        # row is a named tuple now
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
            "status": "NORMAL", # Placeholder or calc logic
            "net_req": row.net_requirement,
            "dos": row.closing_stock
        })
    return result

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
    
    return {"status": "success", "message": "Policy updated", "policy": policy}
