
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models import DimProducts, FactSales, FactForecasts, FactRollingInventory, FactPurchasePlans, FactInventorySnapshots, PlanningDistributionProfile
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

    def run_rolling_calculation(self, sku_list=None, horizon_months=12, profile_id='STD'):
        print(f"Starting Rolling Calculation (Profile: {profile_id})...")
        
        # 1. Fetch Profile Logic
        profile = self.db.query(PlanningDistributionProfile).filter_by(profile_id=profile_id).first()
        ratios = [0.25, 0.25, 0.25, 0.25] # Default
        if profile:
            ratios = [profile.week_1_ratio, profile.week_2_ratio, profile.week_3_ratio, profile.week_4_ratio]
            # print(f"Using Distribution Profile: {profile.profile_name} {ratios}")

        # 1b. Fetch Planning Policy (Safety Stock Days)
        from backend.models import PlanningPolicies
        policy = self.db.query(PlanningPolicies).filter_by(is_default=True).first()
        if not policy:
            policy = self.db.query(PlanningPolicies).first() # Fallback
        
        # Safety Stock Policy (Days or Weeks?) - User asked for "3 Months" ~ 90 Days
        policy_days = policy.safety_stock_days if policy else 90 # Fallback to 90
        print(f"Using Planning Policy: {policy.policy_name if policy else 'Default'} ({policy_days} days)")
        
        # 2. Get Products to Process
        query = self.db.query(DimProducts)
        if sku_list:
            query = query.filter(DimProducts.sku_id.in_(sku_list))
        products = query.all()
        
        today = date.today()
        current_year = today.year
        current_month = today.month
        
        for p in products:
            # print(f"Processing SKU: {p.sku_id}")
            
            # --- A. INITIAL STATE ---
            # TODO: Fetch real opening stock from Warehouse Snapshot or API
            # For now, using 100 or previous closing if exists
            current_stock = 100 
            
            # Try to get existing Opening Stock from last month/latest record?
            # For simplicity in this run, we reset or use a "Stock Snapshot" if we had one.
            # Let's assume 'current_stock' comes from FactInventorySnapshots (Latest)
            latest_snap = self.db.query(FactInventorySnapshots).filter(FactInventorySnapshots.sku_id == p.sku_id).first()
            if latest_snap:
                current_stock = latest_snap.quantity_on_hand
            
            rolling_open = current_stock
            
            # --- B. ROLLING LOOP (Months -> 4 Weeks) ---
            
            # Iterate through horizon_months
            # We start from current month
            
            iter_y = current_year
            iter_m = current_month
            
            for m_offset in range(horizon_months):
                periods = self.get_period_date_ranges(iter_y, iter_m)
                
                # Fetch Monthly Forecast ONCE for efficiency (Optimization)
                # ... (Or just query inside loop)
                
                # Distribution Ratios
                
                # Pre-fetch existing rolling records for this SKU to check for Locked/Manual items
                existing_records_map = {}
                existing_recs = self.db.query(FactRollingInventory).filter(
                     FactRollingInventory.sku_id == p.sku_id,
                     FactRollingInventory.bucket_date >= date(iter_y, iter_m, 1) # Optimization? Just fetch all or from start
                ).all()
                for r in existing_recs:
                    existing_records_map[r.bucket_date] = r

                for w_idx, (p_start, p_end) in enumerate(periods):
                    bucket_key = p_start # Use start date as key
                    
                    # CHECK MANUAL OVERRIDE
                    existing_rec = existing_records_map.get(bucket_key)
                    is_manual = False
                    if existing_rec and existing_rec.is_manual_opening:
                        rolling_open = existing_rec.opening_stock
                        is_manual = True
                        # print(f"Using Manual Opening for {p.sku_id} on {bucket_key}: {rolling_open}")
                    
                    # 1. DEMAND LOGIC
                    # Is this period in the past or current?
                    is_past = p_end < today
                    is_current = p_start <= today <= p_end
                    
                    actual_sold = 0
                    forecast_demand = 0
                    
                    # Fetch Forecast for this Month -> Apply Ratio
                    total_month_forecast = self.db.query(func.sum(FactForecasts.quantity_predicted))\
                        .filter(FactForecasts.sku_id == p.sku_id)\
                        .filter(func.extract('month', FactForecasts.forecast_date) == iter_m)\
                        .filter(func.extract('year', FactForecasts.forecast_date) == iter_y)\
                        .scalar() or 0
                        
                    # Fallback if no forecast
                    if total_month_forecast == 0: total_month_forecast = 40 
                    
                    ratio = ratios[w_idx] if w_idx < 4 else 0.25
                    forecast_demand = total_month_forecast * ratio
                    
                    # Fetch ACTUAL SALES (FactSales) for this period
                    actual_sales_query = self.db.query(func.sum(FactSales.quantity))\
                        .filter(FactSales.sku_id == p.sku_id)\
                        .filter(FactSales.order_date >= p_start)\
                        .filter(FactSales.order_date <= p_end)\
                        .scalar() or 0
                    
                    actual_sold = float(actual_sales_query)
                    
                    # 2. SUPPLY LOGIC (PURCHASES)
                    from backend.models import FactPurchases
                    
                    # Fetch Actual Purchases
                    actual_import_query = self.db.query(func.sum(FactPurchases.quantity))\
                        .filter(FactPurchases.sku_id == p.sku_id, FactPurchases.purchase_type == 'ACTUAL')\
                        .filter(FactPurchases.order_date >= p_start)\
                        .filter(FactPurchases.order_date <= p_end)\
                        .scalar() or 0
                    actual_import = float(actual_import_query)
                    
                    # Fetch Planned Purchases (Incoming)
                    planned_import_query = self.db.query(func.sum(FactPurchases.quantity))\
                        .filter(FactPurchases.sku_id == p.sku_id, FactPurchases.purchase_type == 'PLANNED')\
                        .filter(FactPurchases.order_date >= p_start)\
                        .filter(FactPurchases.order_date <= p_end)\
                        .scalar() or 0
                    incoming_planned = float(planned_import_query)
                    
                    # PRIORITY RULE: If actual import exists (>0), ignore planned. If not, use planned.
                    effective_incoming = 0
                    if actual_import > 0:
                        effective_incoming = actual_import
                    else:
                        effective_incoming = incoming_planned
                        
                    # Incoming for calculation (display separate but use effective for closing)
                    incoming = effective_incoming 
 
                    # Outflow Logic
                    outflow = 0
                    if is_past:
                        outflow = actual_sold
                    elif is_current:
                        outflow = max(actual_sold, forecast_demand) 
                    else:
                        outflow = forecast_demand
                    
                    # 3. CLOSING
                    # NetReq Logic
                    avg_daily = outflow / 7 if outflow > 0 else 0.1
                    target_stock = avg_daily * policy_days
                    
                    closing = rolling_open + incoming + planned - outflow
                    
                    # Recalculate Net Req
                    net_req = 0
                    if closing < target_stock:
                        net_req = target_stock - closing
                        if p.moq and net_req < p.moq: net_req = p.moq
                        # Only generate plan for FUTURE
                        if not is_past: 
                            planned = net_req
                            closing = rolling_open + incoming + planned - outflow
                        else:
                            planned = 0 # Cannot plan for past
                    else:
                         planned = 0 # No need
                    
                    # 4. PERSIST
                    # Merge Logic (Upsert) to preserve ID but update fields
                    
                    # Check if we need to replace or update
                    # Since we want to preserve 'is_manual_opening', we should be careful.
                    # existing_rec was fetched earlier.
                    
                    if existing_rec:
                        existing_rec.opening_stock = rolling_open
                        existing_rec.forecast_demand = forecast_demand
                        existing_rec.incoming_supply = incoming_planned # Store raw
                        existing_rec.planned_supply = planned
                        existing_rec.actual_sold_qty = actual_sold
                        existing_rec.actual_imported_qty = actual_import
                        existing_rec.closing_stock = closing
                        existing_rec.min_stock_policy = target_stock
                        existing_rec.net_requirement = net_req if planned > 0 else 0
                        existing_rec.status = 'OK'
                        existing_rec.updated_at = datetime.now()
                        # is_manual_opening remains as is
                    else:
                         rec = FactRollingInventory(
                            sku_id=p.sku_id,
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
                            is_manual_opening=False
                        )
                         self.db.add(rec)
                    
                    # ROLLOVER
                    rolling_open = closing

                # Next Month
                if iter_m == 12:
                    iter_m = 1
                    iter_y += 1
                else:
                    iter_m += 1
            
            self.db.commit()
            
        print("Rolling Calculation Complete.")
