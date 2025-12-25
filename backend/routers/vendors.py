
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.database import get_db
from backend.services.supplier_intelligence import SupplierIntelligenceService

router = APIRouter(
    prefix="/api/vendors",
    tags=["Vendor Intelligence"],
)

@router.post("/performance/generate-mock")
def generate_mock_data(db: Session = Depends(get_db)):
    service = SupplierIntelligenceService(db)
    try:
        return service.generate_mock_performance_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/ranking")
def get_vendor_ranking(db: Session = Depends(get_db)):
    service = SupplierIntelligenceService(db)
    try:
        return service.get_vendor_ranking()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{vendor_id}/performance")
def get_vendor_performance_history(vendor_id: str, db: Session = Depends(get_db)):
    service = SupplierIntelligenceService(db)
    try:
        data = service.get_vendor_history(vendor_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
