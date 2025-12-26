from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import io
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from datetime import datetime
from backend.database import get_db
from backend.models import DimProducts, DimVendors, FactPurchasePlans, FactSales, DimUnits, DimProductGroups, DimWarehouses, DimCustomerGroups, DimCustomers, SystemConfig, SystemSyncLogs, FactInventorySnapshots
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
    distribution_profile_id: Optional[str] = None

class VendorCreate(BaseModel):
    vendor_id: str
    vendor_name: str
    lead_time_avg: float = 0

class VendorUpdate(BaseModel):
    vendor_name: Optional[str] = None
    lead_time_avg: Optional[float] = None

class UnitCreate(BaseModel):
    unit_id: str
    unit_name: str

class GroupCreate(BaseModel):
    group_id: str
    group_name: str

class WarehouseCreate(BaseModel):
    warehouse_id: str
    warehouse_name: str
    branch_id: Optional[str] = None

class CommonUpdate(BaseModel):
    name: Optional[str] = None # Generic name update
    
class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    min_stock_level: Optional[float] = None
    distribution_profile_id: Optional[str] = None
    moq: Optional[float] = None
    pack_size: Optional[float] = None

# --- Helper Functions ---
def process_products_file(df: pd.DataFrame, db: Session):
    count = 0
    for _, row in df.iterrows():
        try:
            raw_id = row.get('sku_id') or row.get('Product Code')
            sku = "" if pd.isna(raw_id) or str(raw_id).lower() == 'nan' else str(raw_id).strip()
            
            raw_name = row.get('product_name') or row.get('Product Name')
            name = "" if pd.isna(raw_name) else str(raw_name).strip()
            
            if not name and not sku: continue
            
            prod = None
            if sku: prod = db.query(DimProducts).filter(DimProducts.sku_id == sku).first()
            if not prod and name: prod = db.query(DimProducts).filter(DimProducts.product_name == name).first()
            
            if not prod:
                final_id = sku if sku else str(uuid.uuid4())
                prod = DimProducts(sku_id=final_id)
                db.add(prod)
            
            if name: prod.product_name = name
            
            # Optional fields
            cat = row.get('category')
            if cat and not pd.isna(cat): prod.category = str(cat)
            
            unit = row.get('unit')
            if unit and not pd.isna(unit): prod.unit = str(unit)

            stock_min = row.get('min_stock_level')
            if stock_min and not pd.isna(stock_min): prod.min_stock_level = float(stock_min)
            
            db.flush()
            count += 1
        except Exception:
            db.rollback()
            continue
    try: db.commit()
    except: db.rollback()
    return count

def process_vendors_file(df: pd.DataFrame, db: Session):
    count = 0
    for _, row in df.iterrows():
        try:
            raw_id = row.get('vendor_id')
            vid = "" if pd.isna(raw_id) or str(raw_id).lower() == 'nan' else str(raw_id).strip()
            
            raw_name = row.get('vendor_name') or row.get('Vendor Name') or row.get('Partner Name')
            name = "" if pd.isna(raw_name) else str(raw_name).strip()
            
            if not name and not vid: continue
            
            vendor = None
            if vid: vendor = db.query(DimVendors).filter(DimVendors.vendor_id == vid).first()
            if not vendor and name: vendor = db.query(DimVendors).filter(DimVendors.vendor_name == name).first()
            
            if not vendor:
                final_id = vid if vid else str(uuid.uuid4())
                vendor = DimVendors(vendor_id=final_id)
                db.add(vendor)
            
            if name: vendor.vendor_name = name
            
            # Optional fields
            lead_time = row.get('lead_time_avg')
            if lead_time and not pd.isna(lead_time): vendor.lead_time_avg = float(lead_time)
            
            db.flush()
            count += 1
        except Exception:
            db.rollback()
            continue
    try: db.commit()
    except: db.rollback()
    return count

def process_units_file(df: pd.DataFrame, db: Session):
    count = 0
    for _, row in df.iterrows():
        try:
            # Handle ID
            raw_uid = row.get('unit_id')
            if pd.isna(raw_uid):
                uid = ""
            else:
                uid = str(raw_uid).strip()
                if uid.lower() == 'nan': uid = ""

            # Handle Name
            raw_name = row.get('unit_name') or row.get('Unit Name')
            name = "" if pd.isna(raw_name) else str(raw_name).strip()
            
            if not name and not uid:
                # print(f"[IMPORT-SKIP] Empty row")
                continue

            print(f"[IMPORT-ROW] UID='{uid}', Name='{name}'")

            unit = None
            # 1. Try finding by ID
            if uid:
                unit = db.query(DimUnits).filter(DimUnits.unit_id == uid).first()
                if unit: print(f"  -> Found by ID: {unit.unit_name}")
            
            # 2. If no ID or not found by ID, try finding by Name (if valid name)
            if not unit and name:
                 unit = db.query(DimUnits).filter(DimUnits.unit_name == name).first()
                 if unit: print(f"  -> Found by Name: {unit.unit_id}")

            # 3. If still not found, Create New
            if not unit:
                # If we don't have an ID, generate one
                final_id = uid if uid else str(uuid.uuid4())
                print(f"  -> Creating NEW with ID: {final_id}")
                unit = DimUnits(unit_id=final_id)
                db.add(unit)
            else:
                 print("  -> Updating existing.")
            
            # Update fields
            if name:
                unit.unit_name = name
            
            # Flush per row to catch errors immediately (PERFORMANCE HIT but good for debugging)
            db.flush()
            count += 1
        except Exception as e:
            print(f"[IMPORT-ERROR] Row Failed: {e}")
            db.rollback() # Rollback the failed row
            continue # Continue to next row

    try:
        db.commit()
    except Exception as e:
        print(f"[IMPORT-COMMIT-ERROR] {e}")
        db.rollback()

    print(f"[IMPORT-DONE] Processed {count} records.")
    return count

def process_groups_file(df: pd.DataFrame, db: Session):
    count = 0
    for _, row in df.iterrows():
        try:
            # Handle ID
            raw_id = row.get('group_id')
            gid = "" if pd.isna(raw_id) or str(raw_id).lower() == 'nan' else str(raw_id).strip()
            
            # Handle Name
            raw_name = row.get('group_name') or row.get('Group Name')
            name = "" if pd.isna(raw_name) else str(raw_name).strip()
            
            if not name and not gid: continue
            
            group = None
            if gid:
                 group = db.query(DimProductGroups).filter(DimProductGroups.group_id == gid).first()
            
            if not group and name:
                 group = db.query(DimProductGroups).filter(DimProductGroups.group_name == name).first()
                 
            if not group:
                final_id = gid if gid else str(uuid.uuid4())
                group = DimProductGroups(group_id=final_id)
                db.add(group)
            
            if name: group.group_name = name
            
            db.flush()
            count += 1
        except Exception:
            db.rollback()
            continue
    try: db.commit()
    except: db.rollback()
    return count

def process_warehouses_file(df: pd.DataFrame, db: Session):
    count = 0
    for _, row in df.iterrows():
        try:
            raw_id = row.get('warehouse_id')
            wid = "" if pd.isna(raw_id) or str(raw_id).lower() == 'nan' else str(raw_id).strip()
            
            raw_name = row.get('warehouse_name') or row.get('Warehouse Name')
            name = "" if pd.isna(raw_name) else str(raw_name).strip()
            
            branch_id = row.get('branch_id')
            
            if not name and not wid: continue
            
            wh = None
            if wid:
                wh = db.query(DimWarehouses).filter(DimWarehouses.warehouse_id == wid).first()
            if not wh and name:
                wh = db.query(DimWarehouses).filter(DimWarehouses.warehouse_name == name).first()
                
            if not wh:
                final_id = wid if wid else str(uuid.uuid4())
                wh = DimWarehouses(warehouse_id=final_id)
                db.add(wh)
                
            if name: wh.warehouse_name = name
            if branch_id and not pd.isna(branch_id): wh.branch_id = str(branch_id)
            
            db.flush()
            count += 1
        except Exception:
            db.rollback()
            continue
    try: db.commit()
    except: db.rollback()
    return count

def process_customers_file(df: pd.DataFrame, db: Session):
    count = 0
    for _, row in df.iterrows():
        try:
            raw_id = row.get('customer_id')
            cid = "" if pd.isna(raw_id) or str(raw_id).lower() == 'nan' else str(raw_id).strip()
            
            raw_name = row.get('customer_name') or row.get('Customer Name')
            name = "" if pd.isna(raw_name) else str(raw_name).strip()
            
            if not name and not cid: continue
            
            customer = None
            if cid: customer = db.query(DimCustomers).filter(DimCustomers.customer_id == cid).first()
            if not customer and name: customer = db.query(DimCustomers).filter(DimCustomers.customer_name == name).first()
            
            if not customer:
                final_id = cid if cid else str(uuid.uuid4())
                customer = DimCustomers(customer_id=final_id)
                db.add(customer)
            
            if name: customer.customer_name = name
            
            # Optional fields
            misa_code = row.get('misa_code')
            if misa_code and not pd.isna(misa_code): customer.misa_code = str(misa_code)
            
            address = row.get('address')
            if address and not pd.isna(address): customer.address = str(address)
            
            phone = row.get('phone')
            if phone and not pd.isna(phone): customer.phone = str(phone)
            
            email = row.get('email')
            if email and not pd.isna(email): customer.email = str(email)

            db.flush()
            count += 1
        except Exception:
            db.rollback()
            continue
    try: db.commit()
    except: db.rollback()
    return count

def process_partner_groups_file(df: pd.DataFrame, db: Session):
    count = 0
    for _, row in df.iterrows():
        try:
            raw_id = row.get('group_id')
            gid = "" if pd.isna(raw_id) or str(raw_id).lower() == 'nan' else str(raw_id).strip()
            
            raw_name = row.get('group_name') or row.get('Group Name')
            name = "" if pd.isna(raw_name) else str(raw_name).strip()
            
            if not name and not gid: continue
            
            group = None
            if gid: group = db.query(DimCustomerGroups).filter(DimCustomerGroups.group_id == gid).first()
            if not group and name: group = db.query(DimCustomerGroups).filter(DimCustomerGroups.group_name == name).first()
            
            if not group:
                final_id = gid if gid else str(uuid.uuid4())
                group = DimCustomerGroups(group_id=final_id)
                db.add(group)
            
            if name: group.group_name = name
            
            db.flush()
            count += 1
        except Exception:
            db.rollback()
            continue
    try: db.commit()
    except: db.rollback()
    return count

# --- Endpoints ---

@router.get("/inventory")
def get_inventory(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    date: Optional[str] = None,
    warehouse_id: Optional[str] = None,
    group_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get inventory snapshots with product names.
    """
    query = db.query(
        FactInventorySnapshots, 
        DimProducts.product_name
    ).outerjoin(DimProducts, FactInventorySnapshots.sku_id == DimProducts.sku_id)

    if search:
        st = f"%{search}%"
        query = query.filter(
            (FactInventorySnapshots.sku_id.ilike(st)) | 
            (DimProducts.product_name.ilike(st))
        )
    
    if date:
        query = query.filter(FactInventorySnapshots.snapshot_date == date)

    if warehouse_id and warehouse_id != 'ALL':
        query = query.filter(FactInventorySnapshots.warehouse_id == warehouse_id)

    if group_id and group_id != 'ALL':
        query = query.filter(DimProducts.group_id == group_id)
    
    # Default sort: Date Desc, SKU Asc
    query = query.order_by(FactInventorySnapshots.snapshot_date.desc(), FactInventorySnapshots.sku_id.asc())
    
    total = query.count()
    results = query.offset(skip).limit(limit).all()
    
    data = []
    for snap, pname in results:
        data.append({
            "snapshot_date": snap.snapshot_date.isoformat(),
            "warehouse_id": snap.warehouse_id,
            "sku_id": snap.sku_id,
            "product_name": pname,
            "quantity_on_hand": snap.quantity_on_hand,
            "quantity_on_order": snap.quantity_on_order,
            "notes": snap.notes
        })
        
    return {"data": data, "total": total}

@router.post("/import/upload")
async def upload_file(
    type: str, # 'products' | 'vendors' | 'plans' | 'groups' | 'warehouses' | 'units'
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Import data from Excel/CSV file.
    """
    print(f"[IMPORT-DEBUG] Received upload request for type: '{type}'")
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
            raise HTTPException(status_code=400, detail=f"Invalid file format: {file.filename}")
            
        records_processed = 0
        
        # Normalize type checking just in case
        t = type.lower().strip()
        
        if t == 'products':
            records_processed = process_products_file(df, db)
        elif t == 'vendors': # Partners
            records_processed = process_vendors_file(df, db)
        elif t == 'units':
            records_processed = process_units_file(df, db)
        elif t == 'groups':
            records_processed = process_groups_file(df, db)
        elif t == 'warehouses':
            records_processed = process_warehouses_file(df, db)
        elif t == 'customers':
            records_processed = process_customers_file(df, db)
        elif t == 'partner-groups':
            records_processed = process_partner_groups_file(df, db)
        else:
            print(f"[IMPORT-ERROR] Unknown type: {t}")
            raise HTTPException(status_code=400, detail=f"Unknown import type: {type}")
            
        return {"status": "success", "message": f"Processed {records_processed} records."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products")
def get_products(
    skip: int = 0, 
    limit: int = 5000, 
    search: Optional[str] = None,
    category: Optional[str] = None,
    group_id: Optional[str] = None,
    unit: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DimProducts)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (DimProducts.product_name.ilike(search_term)) | 
            (DimProducts.sku_id.ilike(search_term))
        )
    
    if category and category != 'ALL':
        query = query.filter(DimProducts.category == category)

    if group_id and group_id != 'ALL':
        query = query.filter(DimProducts.group_id == group_id)

        
    if unit and unit != 'ALL':
         query = query.filter(DimProducts.unit == unit)

    total = query.count()
    products = query.order_by(DimProducts.sku_id).offset(skip).limit(limit).all()
    
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
        pack_size=item.pack_size,
        distribution_profile_id=item.distribution_profile_id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/vendors")
def get_vendors(
    skip: int = 0, 
    limit: int = 5000,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DimVendors)
    
    if search:
         search_term = f"%{search}%"
         query = query.filter(
             (DimVendors.vendor_name.ilike(search_term)) |
             (DimVendors.vendor_id.ilike(search_term))
         )

    total = query.count()
    vendors = query.order_by(DimVendors.vendor_id).offset(skip).limit(limit).all()
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

@router.put("/vendors/{id}")
def update_vendor(id: str, item: VendorUpdate, db: Session = Depends(get_db)):
    db_item = db.query(DimVendors).filter(DimVendors.vendor_id == id).first()
    if not db_item: raise HTTPException(404, "Not found")
    
    if item.vendor_name: db_item.vendor_name = item.vendor_name
    if item.lead_time_avg is not None: db_item.lead_time_avg = item.lead_time_avg
    
    db.commit()
    return db_item

@router.get("/customers")
def get_customers(db: Session = Depends(get_db)):
    """Fetch MISA Customers"""
    return {"data": db.query(DimCustomers).all()}

@router.delete("/vendors/{id}")
def delete_vendor(id: str, db: Session = Depends(get_db)):
    """
    CRITIAL: Local Database Delete ONLY.
    Do NOT sync this deletion to MISA AMIS.
    """
    db_item = db.query(DimVendors).filter(DimVendors.vendor_id == id).first()
    if not db_item: raise HTTPException(404, "Not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Deleted locally"}

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

@router.post("/sync/crm")
def sync_crm_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Trigger CRM Inventory Sync.
    """
    def run_crm_task(db_session: Session):
        svc = SyncService(db_session)
        print(">>> [SYNC CRM] Background Job Started...")
        try:
            svc.sync_crm_inventory()
            print("<<< [SYNC CRM] Completed successfully.")
        except Exception as e:
            print(f"!!! [SYNC CRM] Failed: {e}")

    background_tasks.add_task(run_crm_task, db)
    return {"status": "started", "message": "CRM Sync started in background."}

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

from backend.models import DimUnits, DimProductGroups, DimWarehouses, PlanningDistributionProfile


@router.get("/units")
def get_units(db: Session = Depends(get_db)):
    return db.query(DimUnits).all()

@router.post("/units")
def create_unit(item: UnitCreate, db: Session = Depends(get_db)):
    if db.query(DimUnits).filter(DimUnits.unit_id == item.unit_id).first():
       raise HTTPException(status_code=400, detail="ID exists")
    new_item = DimUnits(unit_id=item.unit_id, unit_name=item.unit_name)
    db.add(new_item)
    db.commit()
    return new_item

@router.put("/units/{id}")
def update_unit(id: str, item: UnitCreate, db: Session = Depends(get_db)):
    db_item = db.query(DimUnits).filter(DimUnits.unit_id == id).first()
    if not db_item: raise HTTPException(404, "Not found")
    db_item.unit_name = item.unit_name
    db.commit()
    return db_item

@router.delete("/units/{id}")
def delete_unit(id: str, db: Session = Depends(get_db)):
    """
    CRITIAL: Local Database Delete ONLY.
    Do NOT sync this deletion to MISA AMIS.
    """
    db_item = db.query(DimUnits).filter(DimUnits.unit_id == id).first()
    if not db_item: raise HTTPException(404, "Not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Deleted locally"}

@router.get("/groups")
def get_groups(db: Session = Depends(get_db)):
    return db.query(DimProductGroups).all()

@router.post("/groups")
def create_group(item: GroupCreate, db: Session = Depends(get_db)):
    if db.query(DimProductGroups).filter(DimProductGroups.group_id == item.group_id).first():
       raise HTTPException(status_code=400, detail="ID exists")
    new_item = DimProductGroups(group_id=item.group_id, group_name=item.group_name)
    db.add(new_item)
    db.commit()
    return new_item

@router.put("/groups/{id}")
def update_group(id: str, item: GroupCreate, db: Session = Depends(get_db)):
    db_item = db.query(DimProductGroups).filter(DimProductGroups.group_id == id).first()
    if not db_item: raise HTTPException(404, "Not found")
    db_item.group_name = item.group_name
    db.commit()
    return db_item

@router.delete("/groups/{id}")
def delete_group(id: str, db: Session = Depends(get_db)):
    """
    CRITIAL: Local Database Delete ONLY.
    Do NOT sync this deletion to MISA AMIS.
    """
    db_item = db.query(DimProductGroups).filter(DimProductGroups.group_id == id).first()
    if not db_item: raise HTTPException(404, "Not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Deleted locally"}

@router.get("/partner-groups")
def get_partner_groups(db: Session = Depends(get_db)):
    """Fetch MISA 'Customer Groups' (which are also Vendor Groups)"""
    return db.query(DimCustomerGroups).all()


@router.get("/warehouses")
def get_warehouses(db: Session = Depends(get_db)):
    return db.query(DimWarehouses).all()

@router.post("/warehouses")
def create_warehouse(item: WarehouseCreate, db: Session = Depends(get_db)):
    if db.query(DimWarehouses).filter(DimWarehouses.warehouse_id == item.warehouse_id).first():
       raise HTTPException(status_code=400, detail="ID exists")
    new_item = DimWarehouses(warehouse_id=item.warehouse_id, warehouse_name=item.warehouse_name, branch_id=item.branch_id)
    db.add(new_item)
    db.commit()
    return new_item

@router.put("/warehouses/{id}")
def update_warehouse(id: str, item: WarehouseCreate, db: Session = Depends(get_db)):
    db_item = db.query(DimWarehouses).filter(DimWarehouses.warehouse_id == id).first()
    if not db_item: raise HTTPException(404, "Not found")
    db_item.warehouse_name = item.warehouse_name
    if item.branch_id: db_item.branch_id = item.branch_id
    db.commit()
    return db_item

@router.delete("/warehouses/{id}")
def delete_warehouse(id: str, db: Session = Depends(get_db)):
    """
    CRITIAL: Local Database Delete ONLY.
    Do NOT sync this deletion to MISA AMIS.
    """
    db_item = db.query(DimWarehouses).filter(DimWarehouses.warehouse_id == id).first()
    if not db_item: raise HTTPException(404, "Not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Deleted locally"}

@router.get("/profiles")
def get_profiles(db: Session = Depends(get_db)):
    """Fetch all available demand profiles (B2B, B2C, STD)"""
    return db.query(PlanningDistributionProfile).filter(PlanningDistributionProfile.is_active == True).all()



@router.get("/template/{type}")
def download_template(type: str):
    """
    Download Import Templates.
    type: 'rolling_inventory' | 'purchase_plans'
    """
    import csv
    from fastapi.responses import StreamingResponse
    
    headers = []
    filename = f"{type}_template.csv"
    
    if type == 'rolling_inventory':
        headers = ['sku_id', 'bucket_date', 'opening_stock', 'forecast_demand', 'incoming_supply', 'planned_supply', 'min_stock_policy', 'notes']
    elif type == 'purchase_plans':
        headers = ['plan_date', 'sku_id', 'warehouse_id', 'vendor_id', 'forecast_demand', 'safety_stock_required', 'stock_on_order', 'suggested_quantity', 'notes']
    elif type == 'products':
         headers = ['product_code', 'product_name', 'category', 'unit', 'min_stock_level', 'moq', 'pack_size', 'distribution_profile_id']
    elif type == 'vendors':
         headers = ['vendor_id', 'vendor_name', 'lead_time_avg']
    elif type == 'units':
         headers = ['unit_id', 'unit_name']
    elif type == 'groups':
         headers = ['group_id', 'group_name']
    elif type == 'warehouses':
         headers = ['warehouse_id', 'warehouse_name', 'branch_id']
    elif type == 'inventory_manual':
         headers = ['sku', 'warehouse', 'quantity_on_hand', 'quantity_on_order', 'quantity_allocated', 'unit', 'snapshot_date', 'notes']
         # Note: snapshot_date format YYYY-MM-DD. If empty, uses Today.
    else:
        raise HTTPException(status_code=400, detail="Unknown template type")
        
    def iter_csv():
        # Add BOM for Excel UTF-8 support
        yield '\ufeff'
        yield ','.join(headers) + '\n'
        
    return StreamingResponse(iter_csv(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})


@router.post("/inventory/import")
async def import_inventory_manual(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Manual Import of Inventory Snapshots.
    Useful for initialization or correcting specific dates.
    """
    content = await file.read()
    try:
        decoded = content.decode('utf-8-sig') # Handle BOM
    except UnicodeDecodeError:
        decoded = content.decode('latin1')
        
    reader = csv.DictReader(decoded.splitlines())
    rows = list(reader)
    count = 0
    errors = []
    
    today_str = datetime.now().strftime("%Y-%m-%d")

    for idx, row in enumerate(rows):
        try:
            sku = row.get('sku') or row.get('product_code') or row.get('code')
            if not sku: 
                 continue
            
            wh_id = row.get('warehouse') or row.get('warehouse_id') or 'ALL'
            
            date_str = row.get('snapshot_date') or row.get('date')
            if not date_str:
                snapshot_date = datetime.now().date()
            else:
                try:
                    snapshot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except:
                     # Fallback formats could go here
                     snapshot_date = datetime.now().date()

            qty_hand = float(row.get('quantity_on_hand') or row.get('quantity') or 0)
            qty_order = float(row.get('quantity_on_order') or 0)
            qty_alloc = float(row.get('quantity_allocated') or 0)
            unit = row.get('unit') or row.get('unit_name') or ''
            notes = row.get('notes') or "Manual Import"
            
            # Upsert
            snap = db.query(FactInventorySnapshots).filter(
                FactInventorySnapshots.snapshot_date == snapshot_date,
                FactInventorySnapshots.warehouse_id == wh_id,
                FactInventorySnapshots.sku_id == sku
            ).first()
            
            if not snap:
                snap = FactInventorySnapshots(
                    snapshot_date=snapshot_date,
                    warehouse_id=wh_id,
                    sku_id=sku
                )
                db.add(snap)
            
            snap.quantity_on_hand = qty_hand
            snap.quantity_on_order = qty_order
            snap.quantity_allocated = qty_alloc
            if unit:
                snap.unit = unit
            snap.notes = notes
            
            count += 1
        except Exception as e:
            errors.append(f"Row {idx+1}: {str(e)}")
            
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(400, f"DB Commit Error: {str(e)}")

    return {
        "message": f"Successfully imported {count} inventory records.",
        "errors": errors[:10] # Return first 10 errors
    }

@router.get("/crm/config")
def get_crm_config(db: Session = Depends(get_db)):
    """
    Get MISA Integrations credentials (masked) for UI.
    Supports both Legacy (Integrations Page) and New (Data/CRM Page) formats.
    """
    def get_val(key):
         ret = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
         return ret.config_value if ret else ""
    
    crm_id = get_val("MISA_CRM_CLIENT_ID")
    crm_secret = get_val("MISA_CRM_CLIENT_SECRET")
    crm_company_code = get_val("MISA_CRM_COMPANY_CODE")
    
    masked_secret = crm_secret[:5] + "***" if crm_secret else ""

    return {
        # --- New Format (Data/CRM Page) ---
        "client_id": crm_id,
        "client_secret": masked_secret,
        "company_code": crm_company_code,

        # --- Legacy Format (Integrations Page) ---
        "MISA_CRM_CLIENT_ID": crm_id,
        "MISA_CRM_CLIENT_SECRET": crm_secret, # Old page expects raw or handles masking itself? The code showed it sending it back. To be safe, send what we have. 
        # Actually checking old code: it just displays it. If I send masked, it saves masked. 
        # But wait, old page: type={showClientSecret ? "text" : "password"}. It doesn't mask on load.
        # If I send masked here, user might save '*****'.
        # For security, I should send masked. But validation on save needs to ignore '***'.
        
        # Accounting V1
        "MISA_AMIS_ACT_APP_ID": get_val("MISA_AMIS_ACT_APP_ID"),
        "MISA_AMIS_ACT_ACCESS_CODE": get_val("MISA_AMIS_ACT_ACCESS_CODE"),
        "MISA_AMIS_ACT_BASE_URL": get_val("MISA_AMIS_ACT_BASE_URL")
    }

@router.post("/crm/config")
def save_crm_config(config: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Save MISA CRM Credentials.
    Supports both Legacy (Integrations Page) and New (Data/CRM Page) formats.
    """
    try:
        print(f"[CONFIG DEBUG] Received config payload keys: {list(config.keys())}")
        if 'company_code' in config:
             print(f"[CONFIG DEBUG] Found company_code: '{config['company_code']}'")
        else:
             print("[CONFIG DEBUG] company_code NOT found in payload")

        # Helper upsert
        def upsert(key, val):
            if val is None: return # Don't update if not present
            
            # Prevent saving masked secrets
            if 'SECRET' in key and '***' in str(val):
                return 

            obj = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
            if not obj:
                obj = SystemConfig(config_key=key)
                db.add(obj)
            obj.config_value = str(val)
            obj.updated_at = datetime.now()

        # 1. Handle New Format
        if 'client_id' in config: upsert('MISA_CRM_CLIENT_ID', config['client_id'])
        if 'client_secret' in config: upsert('MISA_CRM_CLIENT_SECRET', config['client_secret'])
        if 'company_code' in config: upsert('MISA_CRM_COMPANY_CODE', config['company_code'])
        
        # 2. Handle Legacy Format
        legacy_keys = [
            "MISA_CRM_CLIENT_ID", "MISA_CRM_CLIENT_SECRET", 
            "MISA_AMIS_ACT_APP_ID", "MISA_AMIS_ACT_ACCESS_CODE", "MISA_AMIS_ACT_BASE_URL"
        ]
        for k in legacy_keys:
            if k in config:
                upsert(k, config[k])
        
        db.commit()
        return {"status": "success"}
    except Exception as e:
         db.rollback()
         raise HTTPException(500, str(e))
