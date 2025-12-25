
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.database import get_db
from backend.services.planning_engine import PlanningEngine
from backend.services.forecasting import ForecastingEngine

router = APIRouter(
    prefix="/api/planning",
    tags=["Planning Engine"],
)

@router.post("/calculate-safety-stock")
def calculate_safety_stock_endpoint(db: Session = Depends(get_db)):
    """
    Trigger calculation of Dynamic Safety Stock for all products.
    Uses sales history to compute Standard Deviation.
    """
    engine = PlanningEngine(db)
    try:
        result = engine.calculate_safety_stock()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-plans")
def generate_plans_endpoint(db: Session = Depends(get_db)):
    """
    Generate Purchase Plans based on current Net Requirements and Constraints.
    """
    engine = PlanningEngine(db)
    try:
        result = engine.generate_purchase_plans()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/forecast")
def generate_forecast(
    sku_id: str = Body(..., embed=True),
    model: str = Body("SMA", embed=True),
    periods: int = Body(30, embed=True),
    db: Session = Depends(get_db)
):
    """
    Generate Demand Forecast for a specific SKU.
    """
    engine = ForecastingEngine(db)
    try:
        return engine.calculate_forecast(sku_id, model, periods)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/{sku_id}")
def get_forecast_data(sku_id: str, db: Session = Depends(get_db)):
    """
    Get Historical Sales vs Forecast for visualization.
    """
    engine = ForecastingEngine(db)
    try:
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from backend.models import FactPurchasePlans
from sqlalchemy import desc

@router.get("/plans")
def get_plans(pending_only: bool = False, db: Session = Depends(get_db)):
    """
    Get all purchase plans.
    """
    query = db.query(FactPurchasePlans)
    
    if pending_only:
        query = query.filter(FactPurchasePlans.status != 'APPROVED')
        
    plans = query.order_by(desc(FactPurchasePlans.created_at)).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": p.plan_id,
                "plan_date": p.plan_date.strftime("%Y-%m-%d"),
                "sku_id": p.sku_id,
                "vendor_id": p.vendor_id,
                "suggested_quantity": p.suggested_quantity,
                "final_quantity": p.final_quantity,
                "total_amount": p.total_amount,
                "status": p.status,
                "notes": p.notes
            }
            for p in plans
        ]
    }
