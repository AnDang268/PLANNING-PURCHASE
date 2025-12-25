
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
    db: Session = Depends(get_db)
):
    # Fetch Data formatted for Matrix (Flattened or List)
    query = db.query(FactRollingInventory, DimProducts)\
        .join(DimProducts, FactRollingInventory.sku_id == DimProducts.sku_id)
        
    if category:
        query = query.filter(DimProducts.category == category)
        
    # Sort for Matrix: Product -> Date
    data = query.order_by(FactRollingInventory.sku_id, FactRollingInventory.bucket_date).all()
    
    # We return flat list, Frontend will pivot it to Matrix (Ag-Grid / TanStack Table)
    result = []
    for row, prod in data:
        result.append({
            "sku_id": row.sku_id,
            "product_name": prod.product_name,
            "category": prod.category,
            "bucket_date": row.bucket_date,
            "opening_stock": row.opening_stock,
            "forecast": row.forecast_demand,
            "incoming": row.incoming_supply,
            "planned": row.planned_supply,
            "closing": row.closing_stock,
            "status": row.status,
            "net_req": row.net_requirement,
            "dos": row.closing_stock # Simplified DOS (Day of Supply) output if needed
        })
    return result
