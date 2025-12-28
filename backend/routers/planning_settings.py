from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import SeasonalFactors
from typing import List
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/planning/settings",
    tags=["Planning Configuration"]
)

class SeasonalFactorUpdate(BaseModel):
    month: int
    demand_multiplier: float
    supplier_delay_days: int
    shipping_delay_days: int
    description: str = None

@router.get("/seasonal")
def get_seasonal_factors(db: Session = Depends(get_db)):
    return db.query(SeasonalFactors).order_by(SeasonalFactors.month).all()

@router.put("/seasonal/update")
def update_seasonal_factors(updates: List[SeasonalFactorUpdate], db: Session = Depends(get_db)):
    try:
        count = 0
        for u in updates:
            item = db.query(SeasonalFactors).filter(SeasonalFactors.month == u.month).first()
            if item:
                item.demand_multiplier = u.demand_multiplier
                item.supplier_delay_days = u.supplier_delay_days
                item.shipping_delay_days = u.shipping_delay_days
                item.description = u.description
                count += 1
        db.commit()
        return {"status": "success", "updated": count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
