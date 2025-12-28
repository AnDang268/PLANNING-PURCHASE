
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models import DimProducts, FactSales, FactForecasts, FactRollingInventory, FactPurchasePlans, FactInventorySnapshots, PlanningDistributionProfile, FactPurchases
from datetime import datetime, timedelta, date
import math

class RollingPlanningEngine:
    def __init__(self, db: Session):
        self.db = db

    def get_period_date_ranges(self, year, month):
        """
        Generate 4 periods for a month:
        - Week 1: 1st - 7th
        - Week 2: 8th - 14th
        - Week 3: 15th - 21st
        - Week 4: 22nd - End
        Returns list of (start_date, end_date)
        """
        import calendar
        d1 = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        
        periods = []
        # Week 1
        periods.append((d1, date(year, month, 7)))
        # Week 2
        periods.append((date(year, month, 8), date(year, month, 14)))
        # Week 3
        periods.append((date(year, month, 15), date(year, month, 21)))
        # Week 4
        periods.append((date(year, month, 22), date(year, month, last_day)))
        
        return periods

    def prefetch_data(self, sku_list, start_date, end_date):
        """
        Fetch all necessary data in bulk for the given SKUs and date range.
        Returns dictionaries optimized for O(1) lookup.
        Handles chunking to avoid SQL Server param limit (2100).
        """
        print(f"Prefetching data for {len(sku_list)} SKUs from {start_date} to {end_date}...")
        
        chunk_size = 500
        sku_chunks = [sku_list[i:i + chunk_size] for i in range(0, len(sku_list), chunk_size)]
        
        forecast_map = {}
        sales_map = {}
        purchases_map = {}
        checkpoint_map = {}
        existing_map = {}
        latest_stock_map = {}

        for i, chunk in enumerate(sku_chunks):
            print(f"  Processing chunk {i+1}/{len(sku_chunks)}...")
            # 1. Forecasts
            print("    Fetching Forecasts...")
            forecasts = self.db.query(FactForecasts).filter(
                FactForecasts.sku_id.in_(chunk),
                FactForecasts.forecast_date >= start_date,
                FactForecasts.forecast_date <= end_date
            ).all()
            for f in forecasts:
                key = (f.sku_id, f.forecast_date.year, f.forecast_date.month)
                forecast_map[key] = forecast_map.get(key, 0) + (f.quantity_predicted or 0)
            
            # 2. Sales
            print("    Fetching Sales...")
            sales = self.db.query(FactSales).filter(
                FactSales.sku_id.in_(chunk),
                FactSales.order_date >= start_date,
                FactSales.order_date <= end_date
            ).all()
            for s in sales:
                d = s.order_date.date() if isinstance(s.order_date, datetime) else s.order_date
                key = (s.sku_id, d)
                sales_map[key] = sales_map.get(key, 0) + (s.quantity or 0)

            # 3. Purchases
            print("    Fetching Purchases...")
            purchases = self.db.query(FactPurchases).filter(
                FactPurchases.sku_id.in_(chunk),
                FactPurchases.order_date >= start_date,
                FactPurchases.order_date <= end_date
            ).all()
            for p in purchases:
                d = p.order_date.date() if isinstance(p.order_date, datetime) else p.order_date
                key = (p.sku_id, d, p.purchase_type)
                purchases_map[key] = purchases_map.get(key, 0) + (p.quantity or 0)

            # 4. Checkpoints
            print("    Fetching Checkpoints...")
            from backend.models import FactOpeningStock
            checkpoints = self.db.query(FactOpeningStock).filter(
                FactOpeningStock.sku_id.in_(chunk),
                FactOpeningStock.stock_date >= start_date
            ).all()
            for c in checkpoints:
                key = (c.sku_id, c.stock_date)
                checkpoint_map[key] = checkpoint_map.get(key, 0) + c.quantity

            # 5. Existing Rolling (for manual edits preservation)
            print("    Fetching Existing Rolling...")
            existing_rolling = self.db.query(FactRollingInventory).filter(
                FactRollingInventory.sku_id.in_(chunk),
                FactRollingInventory.bucket_date >= start_date
                # Should we filter by Profile/Warehouse here or do we fetch ALL and filter in memory?
                # Fetching ALL is safer if we want to update the correct generic map.
                # But wait, prefetch_data signature doesn't have profile/warehouse.
                # Let's keep it generic here, but the KEY in existing_map needs to include profile/warehouse if we want to be precise.
                # For now, let's assume this prefetch is used within a context that might need to be specific.
                # UPDATE: Since run_rolling_calculation is specific, we should probably filter here if we could pass context.
                # But to avoid breaking signature, let's fetch all and filter in the map key.
            ).all()
            for r in existing_rolling:
                # Key needs to include Profile/Warehouse now to avoid collision
                existing_map[(r.sku_id, r.bucket_date, r.profile_id, r.warehouse_id)] = r

            # 7. Purchase Plans (Manual/Fixed Plans) --> [NEW]
            print("    Fetching Purchase Plans...")
            plans = self.db.query(FactPurchasePlans).filter(
                FactPurchasePlans.sku_id.in_(chunk),
                FactPurchasePlans.plan_date >= start_date,
                FactPurchasePlans.plan_date <= end_date
            ).all()
            for pp in plans:
                # Use final_quantity if set, else suggested
                val = pp.final_quantity if pp.final_quantity is not None else pp.suggested_quantity
                if val > 0:
                    key = (pp.sku_id, pp.plan_date)
                    if not hasattr(self, 'purchase_plans_map'): self.purchase_plans_map = {}
                    self.purchase_plans_map[key] = self.purchase_plans_map.get(key, 0) + val

            # 6. Latest Snapshots
            print("    Fetching Snapshots...")
            snapshots = self.db.query(FactInventorySnapshots).filter(
                FactInventorySnapshots.sku_id.in_(chunk)
            ).all()
            for s in snapshots:
                latest_stock_map[s.sku_id] = s.quantity_on_hand

        print("Data prefetch complete.")
        if not hasattr(self, 'purchase_plans_map'): self.purchase_plans_map = {}
        return forecast_map, sales_map, purchases_map, checkpoint_map, existing_map, latest_stock_map, self.purchase_plans_map

    def get_date_range_sum(self, data_map, sku_id, start_date, end_date, p_type=None):
        """Helper to sum values in a date range from a (sku, date) map."""
        total = 0
        # Naive iteration over date range? 
        # Since periods are max 7-8 days, iterating dates is fast enough compared to DB query.
        import pandas as pd # Optional, but standard python loops are fine for 7 days.
        
        curr = start_date
        while curr <= end_date:
            if p_type:
                total += data_map.get((sku_id, curr, p_type), 0)
            else:
                total += data_map.get((sku_id, curr), 0)
            curr += timedelta(days=1)
        return total

    def prune_history(self, months_to_keep=6):
        """
        Delete Rolling Inventory records older than X months.
        Keeps table size manageable.
        """
        try:
            cutoff_date = date.today().replace(day=1) - timedelta(days=30 * months_to_keep)
            print(f"Pruning Rolling Inventory older than {cutoff_date}...")
            
            # Efficient Delete
            # Note: might take time if table is huge. 
            self.db.query(FactRollingInventory).filter(
                FactRollingInventory.bucket_date < cutoff_date
            ).delete(synchronize_session=False)
            
            self.db.commit()
            print("Pruning Complete.")
        except Exception as e:
            self.db.rollback()
            print(f"Pruning Failed: {e}")

    def run_sql_procedure(self, horizon_months=12, profile_id='STD', group_id=None, warehouse_id='ALL', run_date=None):
        """
        Executes the SQL Stored Procedure for high-performance calculation.
        """
        from sqlalchemy import text
        try:
            print(f"Executing Stored Procedure sp_RollingSupplyPlanning (Profile: {profile_id}, Group: {group_id}, Warehouse: {warehouse_id}, Date: {run_date})...")
            # Handle 'ALL' for optional params if passed from UI
            g_param = group_id if group_id != 'ALL' else None
            w_param = warehouse_id if warehouse_id else 'ALL'

            self.db.execute(text("EXEC sp_RollingSupplyPlanning @HorizonMonths=:h, @ProfileID=:p, @GroupID=:g, @WarehouseID=:w, @RunDate=:d"), 
                          {'h': horizon_months, 'p': profile_id, 'g': g_param, 'w': w_param, 'd': run_date})
            self.db.commit()
            print("SQL Calculation Complete.")
        except Exception as e:
            self.db.rollback()
            print(f"SQL Execution Failed: {e}")
            raise e

    def run_rolling_calculation(self, sku_list=None, horizon_months=12, profile_id='STD', group_id=None, warehouse_id='ALL', run_date=None):
        # Legacy Python Method - Keeping for reference or fallback partial updates
        # But for "Run All" or main usage, we prefer SQL now.
        if sku_list is None:
             # If running for ALL, use SQL Procedure for speed
             return self.run_sql_procedure(horizon_months, profile_id, group_id, warehouse_id, run_date)
        
        # ... Only use Python loop for specific SKU list updates ...
        print(f"Starting Rolling Calculation (Profile: {profile_id})... [PYTHON FALLBACK]")
        
        # 1. Fetch Profile Logic
        profile = self.db.query(PlanningDistributionProfile).filter_by(profile_id=profile_id).first()
        ratios = [0.25, 0.25, 0.25, 0.25]
        if profile:
            ratios = [profile.week1, profile.week2, profile.week3, profile.week4]

        # 1b. Fetch Planning Policy
        from backend.models import PlanningPolicies
        policy = self.db.query(PlanningPolicies).filter_by(is_default=True).first()
        if not policy:
            policy = self.db.query(PlanningPolicies).first()
        policy_days = policy.safety_stock_days if policy else 90
        
        # 2. Get Products
        query = self.db.query(DimProducts)
        if sku_list:
            query = query.filter(DimProducts.sku_id.in_(sku_list))
        products = query.all()
        all_sku_ids = [p.sku_id for p in products]
        
        if not all_sku_ids:
            print("No products found.")
            return

        # 3. PREFETCH DATA BULK
        today = run_date if run_date else date.today()
        current_year = today.year
        current_month = today.month
        start_date = date(current_year, current_month, 1)
        
        # Calculate rough end date (horizon_months + 1)
        end_date = start_date
        for _ in range(horizon_months + 1):
             # Just add 32 days roughly to jump months for calculation safe bound
             end_date = end_date + timedelta(days=32)
        end_date = end_date.replace(day=1) - timedelta(days=1) # Last day of horizon

        forecast_map, sales_map, purchases_map, checkpoint_map, existing_map, latest_stock_map = \
            self.prefetch_data(all_sku_ids, start_date, end_date)

        # 4. PROCESSING LOOP (Pure Python)
        
        batch_size = 100
        count = 0
        
        for p in products:
            sku_id = p.sku_id
            
            # Init Stock
            current_stock = latest_stock_map.get(sku_id, 0)
            rolling_open = current_stock
            
            iter_y = current_year
            iter_m = current_month
            
            for m_offset in range(horizon_months):
                periods = self.get_period_date_ranges(iter_y, iter_m)
                
                # Monthly Forecast Total
                total_month_forecast = forecast_map.get((sku_id, iter_y, iter_m), 0)
                if total_month_forecast == 0: total_month_forecast = 40 # Fallback

                for w_idx, (p_start, p_end) in enumerate(periods):
                    bucket_key = p_start
                    
                    # A. OPENING STOCK OVERRIDE
                    # Check checkpoint map - loop through range or check keys?
                    # Checkpoint is specific date? usually 1st of month or specific stock count date.
                    # We check if ANY checkpoint exists within this period range.
                    found_snapshot_qty = None
                    curr_chk = p_start
                    while curr_chk <= p_end:
                         if (sku_id, curr_chk) in checkpoint_map:
                             found_snapshot_qty = checkpoint_map[(sku_id, curr_chk)]
                             break
                         curr_chk += timedelta(days=1)
                    
                    if found_snapshot_qty is not None:
                        rolling_open = found_snapshot_qty

                    # B. MANUAL OVERRIDE (From Existing Record)
                    # Key must match the one created in prefetch
                    existing_rec = existing_map.get((sku_id, bucket_key, profile_id, warehouse_id))
                    if existing_rec and existing_rec.is_manual_opening:
                        if found_snapshot_qty is None:
                            rolling_open = existing_rec.opening_stock
                    
                    # C. DEMAND 
                    is_past = p_end < today
                    is_current = p_start <= today <= p_end
                    
                    ratio = ratios[w_idx] if w_idx < 4 else 0.25
                    forecast_demand = total_month_forecast * ratio
                    
                    actual_sold = self.get_date_range_sum(sales_map, sku_id, p_start, p_end)
                    
                    # D. SUPPLY
                    actual_import = self.get_date_range_sum(purchases_map, sku_id, p_start, p_end, 'ACTUAL')
                    incoming_planned = self.get_date_range_sum(purchases_map, sku_id, p_start, p_end, 'PLANNED')
                    
                    effective_incoming = actual_import if actual_import > 0 else incoming_planned
                    incoming = effective_incoming

                    # E. CLOSING & NET REQ
                    outflow = 0
                    if is_past: outflow = actual_sold
                    elif is_current: outflow = max(actual_sold, forecast_demand)
                    else: outflow = forecast_demand
                    
                    planned = 0
                    avg_daily = outflow / 7 if outflow > 0 else 0.1
                    target_stock = avg_daily * policy_days
                    
                    closing = rolling_open + incoming + planned - outflow
                    
                    net_req = 0
                    if closing < target_stock:
                        net_req = target_stock - closing
                        if p.moq and net_req < p.moq: net_req = p.moq
                        
                        if not is_past:
                            planned = net_req
                            closing = rolling_open + incoming + planned - outflow
                    
                    # F. UPDATE / CREATE OBJECT
                    if existing_rec:
                        existing_rec.opening_stock = rolling_open
                        existing_rec.forecast_demand = forecast_demand
                        existing_rec.incoming_supply = incoming_planned
                        existing_rec.planned_supply = planned
                        existing_rec.actual_sold_qty = actual_sold
                        existing_rec.actual_imported_qty = actual_import
                        existing_rec.closing_stock = closing
                        existing_rec.min_stock_policy = target_stock
                        existing_rec.net_requirement = net_req if planned > 0 else 0
                        existing_rec.status = 'OK'
                        existing_rec.updated_at = datetime.now()
                    else:
                        rec = FactRollingInventory(
                            sku_id=sku_id,
                            bucket_date=bucket_key,
                            opening_stock=rolling_open,
                            forecast_demand=forecast_demand,
                            incoming_supply=incoming_planned,
                            planned_supply=planned,
                            actual_sold_qty=actual_sold,
                            actual_imported_qty=actual_import,
                            closing_stock=closing,
                            min_stock_policy=target_stock,
                            net_requirement=net_req if planned > 0 else 0,
                            status='OK',
                            is_manual_opening=False,
                            profile_id=profile_id,
                            warehouse_id=warehouse_id
                        )
                        self.db.add(rec)
                        # Add to map so next iteration finds it? Not needed for next iteration logic 
                        # but good practice if we were using it for lookback. 
                        # Here logic is sequential: rolling_open = closing (NEXT)
                    
                    # ROLLOVER
                    rolling_open = closing

                # Increment Month
                if iter_m == 12:
                    iter_m = 1
                    iter_y += 1
                else:
                    iter_m += 1
            
            count += 1
            if count % batch_size == 0:
                self.db.commit() # Periodic Commit to avoid massive transaction logs
                print(f"Processed {count} SKUs...")
                
        self.db.commit()
        print("Rolling Calculation Complete.")
