from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Dict, Any, List
import pandas as pd
from datetime import date, datetime
from pydantic import BaseModel

from backend.database import get_db
from backend.services.planning_engine import PlanningEngine
from backend.services.forecasting import ForecastingEngine
from backend.models import FactRollingInventory

router = APIRouter(
    prefix="/api/planning",
    tags=["Planning Engine"],
)

@router.get("/test")
def test_endpoint():
    return {"status": "ok"}

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
    sku_id: str = Body(None, embed=True), # Optional if scope=group
    group_id: str = Body(None, embed=True), # New
    scope: str = Body("product", embed=True), # 'product' | 'group'
    model: str = Body("SMA", embed=True),
    periods: int = Body(30, embed=True),
    db: Session = Depends(get_db)
):
    """
    Generate Demand Forecast.
    """
    engine = ForecastingEngine(db)
    try:
        if scope == 'group':
            if not group_id: raise HTTPException(400, "group_id required for group scope")
            return engine.calculate_group_forecast(group_id, model, periods)
        else:
            if not sku_id: raise HTTPException(400, "sku_id required for product scope")
            return engine.calculate_forecast(sku_id, model, periods)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/data")
def get_forecast_data_query(
    sku_id: str = None, 
    group_id: str = None,
    scope: str = "product",
    db: Session = Depends(get_db)
):
    """
    Get Historical Sales vs Forecast for visualization.
    """
    engine = ForecastingEngine(db)
    try:
        if scope == 'group':
             if not group_id: raise HTTPException(400, "group_id required")
             return engine.get_group_forecast_vs_actual(group_id)
        else:
             if not sku_id: raise HTTPException(400, "sku_id required")
             return engine.get_forecast_vs_actual(sku_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/export")
def export_forecast_excel(
    sku_id: str = None, 
    group_id: str = None,
    scope: str = "product",
    db: Session = Depends(get_db)
):
    """
    Export Forecast Data to Excel.
    """
    import io
    import pandas as pd
    from fastapi.responses import StreamingResponse
    
    engine = ForecastingEngine(db)
    data = []
    filename = "forecast.xlsx"
    
    if scope == 'group':
        if not group_id: raise HTTPException(400, "group_id required")
        data = engine.get_group_forecast_vs_actual(group_id)
        filename = f"forecast_group_{group_id}.xlsx"
    else:
        if not sku_id: raise HTTPException(400, "sku_id required")
        data = engine.get_forecast_vs_actual(sku_id)
        filename = f"forecast_product_{sku_id}.xlsx"
        
    # Convert to DataFrame
    df = pd.DataFrame(data)
    # Rename columns for localized output
    df = df.rename(columns={
        "date": "Ngày (Date)",
        "actual": "Thực tế (Actual)",
        "forecast": "Dự báo (Forecast)"
    })
    
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Forecast Data')
        
    stream.seek(0)
    
    return StreamingResponse(
        stream, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# CONFLICT: Moved to planning_rolling.py
# @router.get("/rolling/matrix")
# def get_rolling_matrix(
#     limit: int = 100,
#     search: str = None,
#     group_id: str = None,
#     warehouse_id: str = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     Get Rolling Inventory Matrix (Pivot View).
#     """
#     engine = PlanningEngine(db)
#     try:
#         data = engine.get_rolling_inventory_matrix(limit=limit, search=search, group_id=group_id, warehouse_id=warehouse_id)
#         return data
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.get("/rolling/profiles")
def get_planning_profiles(db: Session = Depends(get_db)):
    """Fetch profiles for Rolling Inventory Filters"""
    from backend.models import PlanningDistributionProfile
    return db.query(PlanningDistributionProfile).filter(PlanningDistributionProfile.is_active == True).all()

@router.get("/forecast/{sku_id}")
def get_forecast_data_legacy(sku_id: str, db: Session = Depends(get_db)):
    """Legacy Endpoint Support"""
    engine = ForecastingEngine(db)
    return engine.get_forecast_vs_actual(sku_id)

@router.post("/plans/update")
def update_plan_endpoint(
    plan_id: int = Body(..., embed=True),
    final_quantity: float = Body(..., embed=True),
    status: str = Body(None, embed=True),
    notes: str = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    """
    Update a purchase plan (quantity, status, notes).
    """
    engine = PlanningEngine(db)
    try:
        result = engine.update_plan(plan_id, final_quantity, status, notes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plans/import")
def import_plans_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Import Purchase Plans from Excel.
    Expected columns: SKU, Final Quantity, Notes.
    """
    try:
        df = pd.read_excel(file.file)
        # Normalize columns
        df.columns = [c.lower().strip() for c in df.columns]
        
        # Mapping: 'sku_id' or 'mã sku' -> sku_id
        # 'final_quantity' or 'chốt (final)' -> final_quantity
        # 'notes' or 'ghi chú' -> notes
        
        count = 0
        from datetime import datetime
        
        for index, row in df.iterrows():
            sku = None
            qty = None
            notes = None
            
            # Simple column search
            for c in df.columns:
                if 'sku' in c: sku = str(row[c]).strip()
                elif 'final' in c or 'chốt' in c: qty = row[c]
                elif 'note' in c or 'ghi chú' in c: notes = row[c]
            
            if sku and qty is not None:
                # Find the plan (assuming latest pending plan or create new? Let's assume update pending)
                # Logic: Find pending plan for this SKU. If multiples, take latest.
                plan = db.query(FactPurchasePlans).filter(
                    FactPurchasePlans.sku_id == sku,
                    FactPurchasePlans.status != 'APPROVED'
                ).order_by(desc(FactPurchasePlans.created_at)).first()
                
                if plan:
                    try:
                        plan.final_quantity = float(qty)
                        if notes: plan.notes = str(notes)
                        count += 1
                    except:
                        continue
        
        db.commit()
        return {"status": "success", "imported_count": count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@router.post("/plans/approve")
def approve_plan_endpoint(
    plan_id: int = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Approve a purchase plan.
    """
    engine = PlanningEngine(db)
    try:
        result = engine.approve_plan(plan_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/plans/{plan_id}")
def delete_plan_endpoint(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a draft purchase plan.
    """
    engine = PlanningEngine(db)
    try:
        result = engine.delete_plan(plan_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RollingUpdateItem(BaseModel):
    sku_id: str
    warehouse_id: str
    bucket_date: date
    planned_supply: float

@router.post("/rolling/update")
def update_rolling_forecast(
    updates: List[RollingUpdateItem],
    db: Session = Depends(get_db)
):
    """
    Bulk update planned_supply in Rolling Matrix.
    """
    try:
        count = 0
        for item in updates:
            rec = db.query(FactRollingInventory).filter(
                FactRollingInventory.sku_id == item.sku_id,
                FactRollingInventory.warehouse_id == item.warehouse_id,
                FactRollingInventory.bucket_date == item.bucket_date
            ).first()
            if rec:
                rec.planned_supply = item.planned_supply
                rec.updated_at = datetime.now()
                count += 1
            else:
                # Upsert if missing (rare but possible)
                rec = FactRollingInventory(
                    sku_id=item.sku_id,
                    warehouse_id=item.warehouse_id,
                    bucket_date=item.bucket_date,
                    planned_supply=item.planned_supply,
                    updated_at=datetime.now()
                )
                db.add(rec)
                count += 1
        
        db.commit()
        return {"status": "success", "updated": count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

class RollingOpeningUpdate(BaseModel):
    sku_id: str
    warehouse_id: str
    bucket_date: date
    opening_stock: float

@router.post("/rolling/update-opening")
def update_rolling_opening(
    update: RollingOpeningUpdate,
    db: Session = Depends(get_db)
):
    """
    Update Opening Stock Manually and Recalculate.
    """
    try:
        # 1. Update DB
        rec = db.query(FactRollingInventory).filter(
            FactRollingInventory.sku_id == update.sku_id,
            FactRollingInventory.warehouse_id == update.warehouse_id,
            FactRollingInventory.bucket_date == update.bucket_date
        ).first()
        
        if rec:
            rec.opening_stock = update.opening_stock
            rec.is_manual_opening = True
            rec.updated_at = datetime.now()
        else:
            rec = FactRollingInventory(
                sku_id=update.sku_id,
                warehouse_id=update.warehouse_id,
                bucket_date=update.bucket_date,
                opening_stock=update.opening_stock,
                is_manual_opening=True,
                status='OK'
            )
            db.add(rec)
        
        db.commit()
        
        # 2. Trigger Re-Calculation for this SKU
        # This ensures the new opening stock propagates to closing and next months
        from backend.services.rolling_calc import RollingPlanningEngine
        engine = RollingPlanningEngine(db)
        engine.run_rolling_calculation(sku_list=[update.sku_id], horizon_months=12) # Recalc localized
        
        return {"status": "success", "message": "Opening stock updated and plan recalculated."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

from backend.models import FactPurchasePlans, DimProducts

@router.get("/plans")
def get_plans(
    skip: int = 0,
    limit: int = 20,
    pending_only: bool = False,
    search: str = None, # SKU filter
    group_id: str = None, # Group filter
    db: Session = Depends(get_db)
):
    """
    Get all purchase plans with filtering and pagination.
    """
    try:
        query = db.query(FactPurchasePlans).join(DimProducts, FactPurchasePlans.sku_id == DimProducts.sku_id)
        
        if pending_only:
            query = query.filter(FactPurchasePlans.status != 'APPROVED')
            
        if search:
            st = f"%{search}%"
            query = query.filter(FactPurchasePlans.sku_id.ilike(st))
            
        if group_id and group_id != "ALL":
            query = query.filter(DimProducts.group_id == group_id)
            
        total = query.count()
        plans = query.order_by(desc(FactPurchasePlans.created_at)).offset(skip).limit(limit).all()
    
        return {
            "status": "success",
            "total": total,
            "data": [
            {
                "id": p.plan_id,
                "plan_date": p.plan_date.strftime("%Y-%m-%d") if p.plan_date else "",
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
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Serialization Error: {str(e)}")

@router.get("/plans/export")
def export_plans_excel(
    pending_only: bool = False,
    search: str = None,
    group_id: str = None,
    db: Session = Depends(get_db)
):
    """
    Export Purchase Plans to Excel.
    """
    import io
    import pandas as pd
    from fastapi.responses import StreamingResponse
    
    query = db.query(
        FactPurchasePlans.plan_date,
        FactPurchasePlans.sku_id,
        DimProducts.product_name,
        FactPurchasePlans.suggested_quantity,
        FactPurchasePlans.final_quantity,
        FactPurchasePlans.status,
        FactPurchasePlans.notes
    ).join(DimProducts, FactPurchasePlans.sku_id == DimProducts.sku_id)
    
    if pending_only:
        query = query.filter(FactPurchasePlans.status != 'APPROVED')
    if search:
        query = query.filter(FactPurchasePlans.sku_id.ilike(f"%{search}%"))
    if group_id and group_id != "ALL":
        query = query.filter(DimProducts.group_id == group_id)
        
    results = query.order_by(desc(FactPurchasePlans.created_at)).all()
    
    data = []
    for r in results:
        data.append({
            "Ngày (Date)": r.plan_date,
            "Mã SKU": r.sku_id,
            "Tên Hàng": r.product_name,
            "Đề xuất (Suggested)": r.suggested_quantity,
            "Chốt (Final)": r.final_quantity,
            "Trạng thái": r.status,
            "Ghi chú": r.notes
        })
        
    df = pd.DataFrame(data)
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Purchase Plans')
        
    stream.seek(0)
    return StreamingResponse(
        stream, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        headers={"Content-Disposition": "attachment; filename=purchase_plans.xlsx"}
    )
