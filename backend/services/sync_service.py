import time
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import (
    SystemConfig, FactSales, DimProducts, FactInventorySnapshots, SystemSyncLogs, 
    DimCustomers, DimVendors, DimUnits, DimProductGroups, DimCustomerGroups, DimWarehouses
)
# Use the new Client
from backend.amis_accounting_client import AmisAccountingClient
from backend.misa_crm_v2_client import MisaCrmV2Client # [NEW]
from backend.database import engine

class SyncService:
    def __init__(self, db: Session):
        """
        Service đồng bộ dữ liệu Master Data từ MISA AMIS Accounting & CRM.
        """
        self.db = db
        # Load AMIS ACT Config
        self.app_id = self._get_config('MISA_AMIS_ACT_APP_ID')
        self.access_code = self._get_config('MISA_AMIS_ACT_ACCESS_CODE')
        self.org_company_code = "CÔNG TY TNHH KIÊN THÀNH TÍN" 
        self.base_url = self._get_config('MISA_AMIS_ACT_BASE_URL') or "https://actapp.misa.vn"
        
        self.client = AmisAccountingClient(self.app_id, self.access_code, self.org_company_code, self.base_url)
        
        # [NEW] Load CRM Config
        self.crm_client_id = self._get_config('MISA_CRM_CLIENT_ID')
        self.crm_client_secret = self._get_config('MISA_CRM_CLIENT_SECRET')
        self.crm_company_code = self._get_config('MISA_CRM_COMPANY_CODE')
        self.crm_client = None
        if self.crm_client_id and self.crm_client_secret and self.crm_company_code:
             self.crm_client = MisaCrmV2Client(self.crm_client_id, self.crm_client_secret, self.crm_company_code)

        self.seen_groups = set() # Cache for deduplication within a sync run

    def _get_config(self, key):
        config = self.db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        return config.config_value if config else None

    # --- MAIN SYNC ORCHESTRATOR ---
    def sync_all_master_data(self):
        """Run full sync sequence"""
        print("[SYNC] Starting Master Data Sync...")
        try: self.sync_units()
        except Exception as e: print(f"  ! Skip UNITS: {e}")

        try: self.sync_product_groups()
        except Exception as e: print(f"  ! Skip GROUPS: {e}")

        try: self.sync_warehouses()
        except Exception as e: print(f"  ! Skip WAREHOUSES: {e}")

        try: self.sync_customers_and_vendors() # Includes Customer Key/Group
        except Exception as e: print(f"  ! Skip PARTNERS: {e}")

        try: self.sync_products() # Depends on Unit/Group
        except Exception as e: print(f"  ! Skip PRODUCTS: {e}")
        print("[SYNC] Master Data Sync Completed.")

    # --- DICTIONARY SYNC METHODS ---

    def sync_units(self):
        self._generic_sync('SYNC_UNITS', self.client.get_units, self._upsert_unit)

    def sync_product_groups(self):
        self._generic_sync('SYNC_PROD_GROUPS', self.client.get_inventory_item_categories, self._upsert_product_group)

    def sync_warehouses(self):
        self._generic_sync('SYNC_STOCKS', self.client.get_stocks, self._upsert_warehouse)

    def sync_products(self):
        self._generic_sync('SYNC_PRODUCTS', self.client.get_inventory_items, self._upsert_product)

    def sync_customers_and_vendors(self):
        """
        Account Objects (Type 1) contains Mixed Customers and Vendors.
        We fetch ONCE, then route to specific Upsert logic.
        Also extracts Customer Groups implicitly.
        """
        self._generic_sync('SYNC_PARTNERS', self.client.get_account_objects, self._upsert_account_object_dispatcher)

    # --- GENERIC RUNNER ---
    def _generic_sync(self, action_type, fetch_func, upsert_func):
        start_time = datetime.now()
        # Create Log Entry
        log = SystemSyncLogs(source='MISA_ACT', action_type=action_type, status='RUNNING', start_time=start_time)
        self.db.add(log)
        self.db.commit()
        # Keep ID for status updates
        log_id = log.log_id
        
        total_count = 0
        try:
            skip = 0
            take = 500 
            
            while True:
                # 0. Check Cancellation
                # Refresh log status from DB
                current_log = self.db.query(SystemSyncLogs).filter(SystemSyncLogs.log_id == log_id).first()
                if current_log and current_log.status == 'CANCEL_REQUESTED':
                    print(f"  > {action_type}: Cancellation requested. Stopping.")
                    current_log.status = 'CANCELLED'
                    current_log.end_time = datetime.now()
                    self.db.commit()
                    return # Exit function completely

                # 1. Fetch Batch from MISA (WITH RETRY)
                print(f"  > {action_type}: Fetching skip={skip}, take={take}...")
                
                batch = None
                max_retries = 4 # User requested 3 retries (1 initial + 3 retries)
                for attempt in range(max_retries):
                    try:
                        batch = self.client.get_dictionary(
                            data_type=self._get_type_id_from_func(fetch_func), 
                            skip=skip, 
                            take=take
                        )
                        break # Success -> Exit retry loop
                    except Exception as e:
                        print(f"    ! [Attempt {attempt+1}/{max_retries}] Fetch Failed: {e}")
                        if attempt < max_retries - 1:
                            time.sleep(2 * (attempt + 1)) # Backoff
                        else:
                            raise e # Propagate error after max retries ensure breaking generic_sync

                
                fetched_count = len(batch) if batch else 0
                print(f"  > {action_type}: Received {fetched_count} items.")
                
                if not batch: 
                    print(f"  > {action_type}: No more data. Loop finished.")
                    break # No more data
                    
                # 2. Process Batch
                current_batch_count = 0
                seen_ids = set() 
                
                for item in batch:
                    try:
                        upsert_func(item, seen_ids)
                        current_batch_count += 1
                    except Exception as row_err:
                        print(f"    ! Error processing row: {row_err}")
                        self.db.rollback()
                        # Continue to next row
                
                # 3. Commit Batch
                try:
                    self.db.commit() # Commit every page
                    total_count += current_batch_count
                    print(f"  > {action_type}: Processed batch {skip} - {skip + len(batch)} ({current_batch_count} upserted)")
                except Exception as batch_err:
                    print(f"  ! Batch Commit Failed: {batch_err}")
                    self.db.rollback()
                    print(f"  > {action_type}: Retrying batch row-by-row...")
                    
                    # FAILURE POINT 2: seen_ids contains items from the failed batch attempt!
                    # We must clear it because we are re-processing them.
                    seen_ids.clear()

                    # Fallback: Row-by-Row Commit
                    for r_item in batch:
                        try:
                            upsert_func(r_item, seen_ids)
                            self.db.commit()
                            total_count += 1
                        except Exception as single_err:
                            self.db.rollback()
                            print(f"    ! Row Skip: {single_err}")

                # if len(batch) < take:
                #     break # Last batch
                    
                skip += len(batch)
            
            # Final Status Update - Refresh to ensure we don't overwrite
            final_log = self.db.query(SystemSyncLogs).filter(SystemSyncLogs.log_id == log_id).first()
            if final_log.status != 'CANCELLED':
                 final_log.status = 'SUCCESS'
                 final_log.records_processed = total_count
                 final_log.end_time = datetime.now()
                 self.db.commit()
                 print(f"  > {action_type}: DONE. Total {total_count} records.")

        except Exception as e:
            self.db.rollback()
            # New Session for Error Log to avoid rollback issues
            try:
                err_log = self.db.query(SystemSyncLogs).filter(SystemSyncLogs.log_id == log_id).first()
                if err_log:
                    err_log.status = 'ERROR'
                    err_log.error_message = str(e)
                    err_log.end_time = datetime.now()
                    self.db.commit()
            except:
                pass
            print(f"  > {action_type} CRITICAL FAIL: {e}")

    def _get_type_id_from_func(self, func):
        # Helper to map func back to ID for paging loop
        if func == self.client.get_units: return 4
        if func == self.client.get_inventory_item_categories: return 14
        if func == self.client.get_stocks: return 3
        if func == self.client.get_inventory_items: return 2
        if func == self.client.get_account_objects: return 1
        return 0

    # --- UPSERT LOGIC ---

    def _upsert_unit(self, item: dict, seen_ids: set = None) -> bool:
        unit_id = item.get("UnitID")
        unit_name = item.get("UnitName")
        
        # DEBUG UNICODE
        if unit_name and ('Cặp' in unit_name or '?' in unit_name):
            print(f"[UNICODE-DEBUG] Raw UnitName: '{unit_name}' (Codes: {[ord(c) for c in unit_name]})")

        if not unit_id: 
            return False
        
        if seen_ids is not None:
             if unit_id in seen_ids: 
                 return False
             seen_ids.add(unit_id)
             
        obj = self.db.query(DimUnits).filter(DimUnits.unit_id == unit_id).first()
        if not obj:
            obj = DimUnits(unit_id=unit_id)
            self.db.add(obj)
        
        # Check changes
        new_name = data.get('unit_name')
        new_desc = data.get('description')
        
        if obj.unit_name != new_name or obj.description != new_desc:
            obj.unit_name = new_name
            obj.description = new_desc
            obj.updated_at = datetime.now()

    def _upsert_product_group(self, data, seen_ids=None):
        gid = data.get('inventory_category_id') # Type 14 keys
        if not gid: return
        if seen_ids is not None:
             if gid in seen_ids: return
             seen_ids.add(gid)

        obj = self.db.query(DimProductGroups).filter(DimProductGroups.group_id == gid).first()
        if not obj:
            obj = DimProductGroups(group_id=gid)
            self.db.add(obj)
        
        new_name = data.get('inventory_category_name')
        new_code = data.get('inventory_category_code')
        # Map Parent ID: MISA usually returns 'parent_id' or 'ParentID'
        new_parent = data.get('parent_id')
        if not new_parent:
             new_parent = data.get('ParentID')
        
        if (obj.group_name != new_name or 
            obj.misa_code != new_code or
            obj.parent_id != new_parent):
            
            obj.group_name = new_name
            obj.misa_code = new_code
            obj.parent_id = new_parent
            obj.updated_at = datetime.now()

    def _upsert_warehouse(self, data, seen_ids=None):
        wid = data.get('stock_id')
        if not wid: return
        # Simple check - usually few warehouses
        obj = self.db.query(DimWarehouses).filter(DimWarehouses.warehouse_id == wid).first()
        if not obj:
            obj = DimWarehouses(warehouse_id=wid)
            self.db.add(obj)
        
        new_name = data.get('stock_name')
        new_addr = data.get('address')
        
        if obj.warehouse_name != new_name or obj.address != new_addr:
            obj.warehouse_name = new_name
            obj.address = new_addr
            obj.updated_at = datetime.now()

    def _upsert_product(self, data, seen_ids=None):
        sku_id = data.get('inventory_item_code', '')[:50] # DB Limit
        if not sku_id: return
        if seen_ids is not None:
             if sku_id in seen_ids: return
             seen_ids.add(sku_id)
        
        amis_id = data.get('inventory_item_id')
        
        obj = self.db.query(DimProducts).filter(DimProducts.sku_id == sku_id).first()
        if not obj:
            obj = DimProducts(sku_id=sku_id)
            self.db.add(obj)
            
        # Group Mapping: Pick first ID
        g_raw = data.get('inventory_item_category_id_list')
        new_group_id = None
        if g_raw:
             # handle list or string "id;id"
             parts = g_raw.split(';') if isinstance(g_raw, str) else g_raw
             if parts and len(parts) > 0:
                 new_group_id = parts[0]
        
        new_name = data.get('inventory_item_name')
        new_unit = data.get('unit_id')
        
        if (obj.product_name != new_name or 
            obj.amis_act_id != amis_id or 
            obj.base_unit_id != new_unit or 
            obj.group_id != new_group_id):
            
            obj.product_name = new_name
            obj.amis_act_id = amis_id
            obj.base_unit_id = new_unit
            obj.group_id = new_group_id
            obj.updated_at = datetime.now()

    def _upsert_account_object_dispatcher(self, data, seen_ids=None):
        # 1. EXTRACT GROUP
        g_ids = data.get('account_object_group_id_list')
        g_names = data.get('account_object_group_name_list')
        
        primary_group_id = None
        
        if g_ids and g_names:
            # Simplify: Split and Zip
            # Note: MISA returns delimited strings "id1;id2"
             ids = [i.strip() for i in g_ids.split(';')] if isinstance(g_ids, str) else g_ids
             names = g_names.split(';') if isinstance(g_names, str) else g_names
             
             if ids:
                 primary_group_id = ids[0]
                 # Upsert Groups implicit
                 for i, gid in enumerate(ids):
                     gname = names[i] if i < len(names) else "Unknown"
                     self._upsert_customer_group_implicit(gid, gname)

        # We use seen_ids to track account_object_code (Partner ID)
        code = data.get('account_object_code', '')[:50]
        if seen_ids is not None and code:
            if code in seen_ids: return
            seen_ids.add(code)

        # 2. UPSERT CUSTOMER
        if data.get('is_customer'):
            self._upsert_customer(data, primary_group_id)
            
        # 3. UPSERT VENDOR
        if data.get('is_vendor'):
            self._upsert_vendor(data, primary_group_id)

    def _upsert_customer_group_implicit(self, gid, gname):
        if not gid: return
        # FAILURE POINT: If we rollback, this cache is stale.
        # if gid in self.seen_groups: return 
        # self.seen_groups.add(gid)
        
        # Use merge strategy for robust upsert (handles sessions/DB state better)
        # This creates a transient object, merges it into session (finding existing or creating new)
        pending_obj = DimCustomerGroups(group_id=gid)
        obj = self.db.merge(pending_obj)
            
        if obj.group_name != gname:
            obj.group_name = gname
            obj.updated_at = datetime.now()

    def _upsert_customer(self, data, group_id):
        cid = data.get('account_object_code', '')[:50]
        if not cid: return
        
        obj = self.db.query(DimCustomers).filter(DimCustomers.customer_id == cid).first()
        if not obj:
            print(f"    + [NEW-CUST] {cid} - {data.get('account_object_name')}")
            obj = DimCustomers(customer_id=cid)
            self.db.add(obj)
        
        new_name = data.get('account_object_name')
        new_addr = data.get('address')
        new_phone = data.get('tel')
        
        if (obj.customer_name != new_name or 
            obj.group_id != group_id or 
            obj.address != new_addr or 
            obj.phone != new_phone):
            
            # print(f"    * [UPD-CUST] {cid}")
            obj.customer_name = new_name
            obj.misa_code = cid
            obj.address = new_addr
            obj.phone = new_phone
            obj.group_id = group_id
            obj.updated_at = datetime.now()

    def _upsert_vendor(self, data, group_id):
        vid = data.get('account_object_code', '')[:50]
        if not vid: return
        
        obj = self.db.query(DimVendors).filter(DimVendors.vendor_id == vid).first()
        if not obj:
            print(f"    + [NEW-VEND] {vid} - {data.get('account_object_name')}")
            obj = DimVendors(vendor_id=vid)
            self.db.add(obj)
            
        new_name = data.get('account_object_name')
        new_addr = data.get('address')
        new_phone = data.get('tel')
        new_tax = data.get('company_tax_code')
        
        if (obj.vendor_name != new_name or 
            obj.group_id != group_id or 
            obj.address != new_addr or 
            obj.phone != new_phone or 
            obj.tax_code != new_tax):

            # print(f"    * [UPD-VEND] {vid}")
            obj.vendor_name = new_name
            obj.address = new_addr
            obj.phone = new_phone
            obj.tax_code = new_tax
            obj.group_id = group_id
            obj.updated_at = datetime.now()
    # --- CRM SYNC ---
    def sync_crm_inventory(self):
        """
        Sync Inventory from MISA CRM V2 (Per Warehouse).
        Steps:
        1. Fetch list of Stocks (Warehouses).
        2. Iterate and fetch product ledger for each Stock.
        3. Upsert into Fact_Inventory_Snapshots.
        """
        today = datetime.now().date()
        self._create_log("MISA_CRM", "SYNC_INVENTORY", f"Starting Sync for {today}...")

        try:
            # 1. Fetch Stocks
            url_stocks = f"{self.crm_client.base_url}/Stocks"
            headers_stocks = {
                "authorization": f"Bearer {self.crm_client.token or self.crm_client.authenticate()}",
                "clientid": self.crm_client.client_id,
                "companycode": self.crm_client.company_code
            }
            resp_stocks = requests.get(url_stocks, headers=headers_stocks)
            stocks = []
            if resp_stocks.status_code == 200:
                s_data = resp_stocks.json()
                if s_data.get("success") or s_data.get("code") == 0:
                    stocks = s_data.get("data", [])
            
            if not stocks:
                print("! No stocks found or error fetching stocks. Defaulting to 'ALL' sync.")
                # Fallback to previous logic if no stocks (optional, but better to be safe)
                stocks = [{'stock_id': None, 'stock_code': 'ALL', 'stock_name': 'Default'}]

            total_records = 0
            
            for stock in stocks:
                stock_id = stock.get('stock_id') or stock.get('act_database_id')
                stock_code = stock.get('stock_code', 'ALL')
                stock_name = stock.get('stock_name', 'Unknown')
                
                if not stock_id and stock_code != 'ALL':
                    continue # Skip invalid stocks

                print(f"  > Syncing Warehouse: {stock_code} ({stock_name})...")
                
                page = 1
                page_size = 100
                
                while True:
                    try:
                        items = self.crm_client.get_product_ledger(stock_id=stock_id, page=page, page_size=page_size)
                        
                        if not items:
                            break
                        
                        for item in items:
                            try:
                                # Fallback mapping for various API versions
                                sku = item.get('product_code') or item.get('inventory_item_code') or item.get('sku') or item.get('code')
                                # Ensure we use the current loop's warehouse ID
                                wh_id = stock_code 
                                
                                # Correct Keys based on Debug Output
                                qty_hand = item.get('main_stock_quantity') or item.get('quantity') or item.get('balance') or 0
                                qty_order = item.get('order_quantity') or 0
                                qty_alloc = item.get('delivery_quantity') or 0
                                unit = item.get('unit_name') or item.get('unit_id') or item.get('uom_name') or ''
                                
                                if not sku: 
                                    continue

                                # UPSERT into Fact_Inventory_Snapshots
                                snap = self.db.query(FactInventorySnapshots).filter(
                                    FactInventorySnapshots.snapshot_date == today,
                                    FactInventorySnapshots.warehouse_id == wh_id,
                                    FactInventorySnapshots.sku_id == sku
                                ).first()
                                
                                if not snap:
                                    snap = FactInventorySnapshots(
                                        snapshot_date=today,
                                        warehouse_id=wh_id,
                                        sku_id=sku
                                    )
                                    self.db.add(snap)
                                
                                snap.quantity_on_hand = float(qty_hand)
                                snap.quantity_on_order = float(qty_order)
                                snap.quantity_allocated = float(qty_alloc)
                                if unit:
                                    snap.unit = unit
                                snap.notes = f"MISA Sync: {stock_name}"
                            except Exception as row_e:
                                print(f"    ! Error processing row: {row_e}")
                                continue
                        
                        self.db.commit()
                        total_records += len(items)
                        print(f"    - Page {page}: {len(items)} items processed.")
                        page += 1
                        
                    except Exception as page_e:
                        print(f"    ! Error fetching page {page}: {page_e}")
                        break

            self._update_log_success(total_records)
            return True

        except Exception as e:
            self._update_log_error(str(e))
            print(f"SYNC_INVENTORY ERROR: {e}")
            return False
    # --- HELPER LOGGING methods ---
    def _create_log(self, source, action_type):
        log = SystemSyncLogs(source=source, action_type=action_type, status='RUNNING', start_time=datetime.now())
        self.db.add(log)
        self.db.commit()
        return log.log_id

    def _update_log_success(self, log_id, count):
        log = self.db.query(SystemSyncLogs).filter(SystemSyncLogs.log_id == log_id).first()
        if log:
            log.status = 'SUCCESS'
            log.records_processed = count
            log.end_time = datetime.now()
            self.db.commit()

    def _update_log_error(self, log_id, error_msg):
        # Use new session/transaction for error logging to ensure it persists even if main tx rolled back
        try:
            self.db.rollback() # Rollback current transaction
            log = self.db.query(SystemSyncLogs).filter(SystemSyncLogs.log_id == log_id).first()
            if log:
                log.status = 'ERROR'
                log.error_message = str(error_msg)
                log.end_time = datetime.now()
                self.db.add(log) # Ensure attached
                self.db.commit()
        except:
             pass
