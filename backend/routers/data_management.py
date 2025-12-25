from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import io
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from backend.database import get_db
from backend.models import DimProducts, DimVendors, FactPurchasePlans, FactSales
from backend.services.sync_service import SyncService

router = APIRouter(
    prefix="/api/data",
    tags=["Data Management"],
)

# --- Pydantic Models for Manual Creation ---
class ProductCreate(BaseModel):
    sku_id: str
    product_name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    min_stock_level: float = 0
    moq: float = 1
    pack_size: float = 1

class VendorCreate(BaseModel):
    vendor_id: str
    vendor_name: str
    lead_time_avg: float = 0

# --- Helper Functions ---
def process_products_file(df: pd.DataFrame, db: Session):
    count = 0
    # Expected columns: sku_id, product_name, category, unit, min_stock_level
    for _, row in df.iterrows():
        sku = str(row.get('sku_id', '')).strip()
        if not sku: continue
        
        product = db.query(DimProducts).filter(DimProducts.sku_id == sku).first()
        if not product:
            product = DimProducts(sku_id=sku)
            db.add(product)
        
        product.product_name = row.get('product_name', product.product_name)
        product.category = row.get('category', product.category)
        product.unit = row.get('unit', product.unit)
        product.min_stock_level = row.get('min_stock_level', product.min_stock_level)
        product.moq = row.get('moq', getattr(product, 'moq', 1))
        product.pack_size = row.get('pack_size', getattr(product, 'pack_size', 1))
        count += 1
    db.commit()
    return count

def process_vendors_file(df: pd.DataFrame, db: Session):
    count = 0
    # Expected columns: vendor_id, vendor_name, lead_time_avg
    for _, row in df.iterrows():
        vid = str(row.get('vendor_id', '')).strip()
        if not vid: continue
        
        vendor = db.query(DimVendors).filter(DimVendors.vendor_id == vid).first()
        if not vendor:
            vendor = DimVendors(vendor_id=vid)
            db.add(vendor)
            
        vendor.vendor_name = row.get('vendor_name', vendor.vendor_name)
        vendor.lead_time_avg = row.get('lead_time_avg', vendor.lead_time_avg)
        count += 1
    db.commit()
    return count

# --- Endpoints ---

@router.post("/import/upload")
async def upload_file(
    type: str, # 'products' | 'vendors' | 'plans'
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Import data from Excel/CSV file.
    """
    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            # Try utf-8-sig for Excel CSVs, fallback to utf-8 then cp1252
            try:
                df = pd.read_csv(io.BytesIO(contents), encoding='utf-8-sig')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(io.BytesIO(contents), encoding='utf-16')
                except:
                    df = pd.read_csv(io.BytesIO(contents), encoding='cp1252')
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Invalid file format")
            
        records_processed = 0
        if type == 'products':
            records_processed = process_products_file(df, db)
        elif type == 'vendors':
            records_processed = process_vendors_file(df, db)
        else:
            raise HTTPException(status_code=400, detail="Unknown import type")
            
        return {"status": "success", "message": f"Processed {records_processed} records."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products")
def get_products(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    products = db.query(DimProducts).order_by(DimProducts.sku_id).offset(skip).limit(limit).all()
    total = db.query(DimProducts).count()
    return {"data": products, "total": total}

@router.post("/products")
def create_product(item: ProductCreate, db: Session = Depends(get_db)):
    db_item = db.query(DimProducts).filter(DimProducts.sku_id == item.sku_id).first()
    if db_item:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    new_item = DimProducts(
        sku_id=item.sku_id,
        product_name=item.product_name,
        category=item.category,
        unit=item.unit,
        min_stock_level=item.min_stock_level,
        moq=item.moq,
        pack_size=item.pack_size
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/vendors")
def get_vendors(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    vendors = db.query(DimVendors).order_by(DimVendors.vendor_id).offset(skip).limit(limit).all()
    total = db.query(DimVendors).count()
    return {"data": vendors, "total": total}

@router.post("/vendors")
def create_vendor(item: VendorCreate, db: Session = Depends(get_db)):
    db_item = db.query(DimVendors).filter(DimVendors.vendor_id == item.vendor_id).first()
    if db_item:
        raise HTTPException(status_code=400, detail="Vendor ID already exists")
        
    new_item = DimVendors(
        vendor_id=item.vendor_id,
        vendor_name=item.vendor_name,
        lead_time_avg=item.lead_time_avg
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.delete("/reset")
def reset_database(db: Session = Depends(get_db)):
    """
    DANGER: Purges all data from Dimensions and Facts.
    Used for resetting the system.
    """
    try:
        # Delete detailed facts first to avoid foreign key constraints (if any enforced)
        db.query(FactPurchasePlans).delete()
        db.query(FactSales).delete()
        
        # Delete dimensions
        db.query(DimProducts).delete()
        db.query(DimVendors).delete()
        
        db.commit()
        return {"status": "success", "message": "All data has been reset."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks

# ... (Previous imports remain, ensure BackgroundTasks is imported)

@router.post("/sync/misa")
def sync_misa_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Trigger FULL synchronization (All Master Data).
    """
    def run_sync_task(db_session: Session):
        sync_service = SyncService(db_session)
        print(">>> [SYNC FULL] Background Job Started...")
        try:
            sync_service.sync_all_master_data()
            print("<<< [SYNC FULL] Completed successfully.")
        except Exception as e:
            print(f"!!! [SYNC FULL] Failed: {e}")

    background_tasks.add_task(run_sync_task, db)
    return {"status": "started", "message": "Full Sync started in background."}

@router.post("/sync/{type}")
def sync_specific_data(type: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Trigger Granular Sync: 'units', 'groups', 'warehouses', 'partners', 'products'
    """
    valid_types = ['units', 'groups', 'warehouses', 'partners', 'products']
    if type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid sync type. Must be one of {valid_types}")

    def run_granular_task(t: str, db_session: Session):
        svc = SyncService(db_session)
        print(f">>> [SYNC {t.upper()}] Background Job Started...")
        try:
            if t == 'units': svc.sync_units()
            elif t == 'groups': svc.sync_product_groups()
            elif t == 'warehouses': svc.sync_warehouses()
            elif t == 'partners': svc.sync_customers_and_vendors()
            elif t == 'products': svc.sync_products()
            print(f"<<< [SYNC {t.upper()}] Completed successfully.")
        except Exception as e:
             print(f"!!! [SYNC {t.upper()}] Failed: {e}")

    background_tasks.add_task(run_granular_task, type, db)
    return {"status": "started", "message": f"Sync for '{type}' started in background."}

@router.post("/sync/cancel")
def cancel_active_sync(db: Session = Depends(get_db)):
    """
    Cancel any RUNNING sync jobs.
    """
    # Find all running logs
    running_logs = db.query(SystemSyncLogs).filter(SystemSyncLogs.status == 'RUNNING').all()
    count = 0
    for log in running_logs:
        log.status = 'CANCEL_REQUESTED'
        count += 1
    
    db.commit()
    return {"status": "success", "message": f"Requested cancellation for {count} jobs."}

from backend.models import DimUnits, DimProductGroups, DimWarehouses


@router.get("/units")
def get_units(db: Session = Depends(get_db)):
    return db.query(DimUnits).all()

@router.get("/groups")
def get_groups(db: Session = Depends(get_db)):
    return db.query(DimProductGroups).all()

@router.get("/warehouses")
def get_warehouses(db: Session = Depends(get_db)):
    return db.query(DimWarehouses).all()

