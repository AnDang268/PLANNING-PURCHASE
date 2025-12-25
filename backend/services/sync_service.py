import time
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import (
    SystemConfig, FactSales, DimProducts, FactInventorySnapshots, SystemSyncLogs, 
    DimCustomers, DimVendors, DimUnits, DimProductGroups, DimCustomerGroups, DimWarehouses
)
# Use the new Client
from backend.amis_accounting_client import AmisAccountingClient
from backend.database import engine

class SyncService:
    def __init__(self, db: Session):
        """
        Service đồng bộ dữ liệu Master Data từ MISA AMIS Accounting.
        """
        self.db = db
        # Load AMIS ACT Config
        self.app_id = self._get_config('MISA_AMIS_ACT_APP_ID')
        self.access_code = self._get_config('MISA_AMIS_ACT_ACCESS_CODE')
        self.org_company_code = "CÔNG TY TNHH KIÊN THÀNH TÍN" # self._get_config('MISA_AMIS_ACT_ORG_CODE') 
        self.base_url = self._get_config('MISA_AMIS_ACT_BASE_URL') or "https://actapp.misa.vn"
        
        self.client = AmisAccountingClient(self.app_id, self.access_code, self.org_company_code, self.base_url)

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
            take = 50 # Process in smaller batches for safety
            
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

                # 1. Fetch Batch from MISA
                batch = self.client.get_dictionary(
                    data_type=self._get_type_id_from_func(fetch_func), 
                    skip=skip, 
                    take=take
                )
                
                if not batch: 
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
                        # Continue to next row
                
                # 3. Commit Batch
                self.db.commit() # Commit every page
                total_count += current_batch_count
                
                print(f"  > {action_type}: Processed batch {skip} - {skip + len(batch)} ({current_batch_count} upserted)")

                if len(batch) < take:
                    break # Last batch
                    
                skip += take
            
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

    def _upsert_unit(self, data, seen_ids=None):
        uid = data.get('unit_id')
        if not uid: return
        if seen_ids is not None:
             if uid in seen_ids: return
             seen_ids.add(uid)
             
        obj = self.db.query(DimUnits).filter(DimUnits.unit_id == uid).first()
        if not obj:
            obj = DimUnits(unit_id=uid)
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
        # Map Parent ID (Try both 'parent_id' and 'parent_id' from response)
        new_parent = data.get('parent_id') or data.get('parent_id') # Adjust key if needed based on real payload
        
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
             ids = g_ids.split(';') if isinstance(g_ids, str) else g_ids
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
        obj = self.db.query(DimCustomerGroups).filter(DimCustomerGroups.group_id == gid).first()
        if not obj:
            obj = DimCustomerGroups(group_id=gid)
            self.db.add(obj)
            
        if obj.group_name != gname:
            obj.group_name = gname
            obj.updated_at = datetime.now()

    def _upsert_customer(self, data, group_id):
        cid = data.get('account_object_code', '')[:50]
        if not cid: return
        
        obj = self.db.query(DimCustomers).filter(DimCustomers.customer_id == cid).first()
        if not obj:
            obj = DimCustomers(customer_id=cid)
            self.db.add(obj)
        
        new_name = data.get('account_object_name')
        new_addr = data.get('address')
        new_phone = data.get('tel')
        
        if (obj.customer_name != new_name or 
            obj.group_id != group_id or 
            obj.address != new_addr or 
            obj.phone != new_phone):
            
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

            obj.vendor_name = new_name
            obj.address = new_addr
            obj.phone = new_phone
            obj.tax_code = new_tax
            obj.group_id = group_id
            obj.updated_at = datetime.now()
