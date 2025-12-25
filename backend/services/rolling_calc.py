
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models import DimProducts, FactSales, FactForecasts, FactRollingInventory, FactPurchasePlans, FactInventorySnapshots, PlanningDistributionProfile
from datetime import datetime, timedelta, date
import math

class RollingPlanningEngine:
    def __init__(self, db: Session):
        self.db = db

    def run_rolling_calculation(self, sku_list=None, horizon_months=12, profile_id='STD'):
        print(f"Starting Rolling Calculation (Profile: {profile_id})...")
        
        # 1. Fetch Profile Logic
        profile = self.db.query(PlanningDistributionProfile).filter_by(profile_id=profile_id).first()
        ratios = [0.25, 0.25, 0.25, 0.25] # Default
        if profile:
            ratios = [profile.week_1_ratio, profile.week_2_ratio, profile.week_3_ratio, profile.week_4_ratio]
            print(f"Using Distribution Profile: {profile.profile_name} {ratios}")
        
        # 2. Get Products to Process
        query = self.db.query(DimProducts)
        if sku_list:
            query = query.filter(DimProducts.sku_id.in_(sku_list))
        products = query.all()
        
        start_date = date.today()
        start_of_week = start_date - timedelta(days=start_date.weekday())
        
        for p in products:
            # print(f"Processing SKU: {p.sku_id}")
            
            # --- A. INITIAL STATE ---
            # Bypass DB for now to debug 42S22 (Use 100 for proper testing)
            current_stock = 100 
            
            rolling_open = current_stock
            
            # --- B. ROLLING LOOP (Weeks) ---
            for w in range(horizon_months * 4): 
                week_start = start_of_week + timedelta(weeks=w)
                week_end = week_start + timedelta(days=6)
                
                # 1. Demand Calculation (Profile Applied)
                # Query FactForecasts for this MONTH
                # e.g. Sum of forecast_date between month_start and month_end
                month_start = start_of_week + timedelta(weeks=w) 
                month_start = month_start.replace(day=1) # Normalize to 1st of month? 
                # Actually, our Rolling view is Weekly.
                # If FactForecasts is Daily, we sum for the specific week range.
                
                # Fetch sum of forecast for this specific week range
                f_demand_raw = self.db.query(func.sum(FactForecasts.quantity_predicted))\
                    .filter(FactForecasts.sku_id == p.sku_id)\
                    .filter(FactForecasts.forecast_date >= week_start)\
                    .filter(FactForecasts.forecast_date <= week_end)\
                    .scalar() or 0
                
                # If we use Profile Logic (Scenario Planning), we might want to Override the raw daily distribution
                # with our Profile Curve.
                # E.g. WeeklyDemand = TotalMonthlyForecast * WeekRatio
                
                # Strategy: Get Total Demand for the Month containing this week
                current_month_start = week_start.replace(day=1)
                next_month = current_month_start.replace(day=28) + timedelta(days=4)
                current_month_end = next_month - timedelta(days=next_month.day)
                
                total_month_demand = self.db.query(func.sum(FactForecasts.quantity_predicted))\
                    .filter(FactForecasts.sku_id == p.sku_id)\
                    .filter(FactForecasts.forecast_date >= current_month_start)\
                    .filter(FactForecasts.forecast_date <= current_month_end)\
                    .scalar() or 0
                
                # If no forecast, fallback to mock average (for demo data) until user runs forecast
                if total_month_demand == 0:
                   total_month_demand = 40 # Fallback for Demo
                
                # Determine which "Week of Month" this is (0, 1, 2, 3)
                week_idx = w % 4 
                current_ratio = ratios[week_idx] if week_idx < 4 else 0.25
                
                # Dynamic Demand:
                f_demand = total_month_demand * current_ratio
                
                # 2. Existing Supply (Incoming POs)
                incoming = 0 
                
                # 3. Planned Supply
                planned = 0
                
                # 4. Closing Calculation (First Pass)
                closing = rolling_open + incoming + planned - f_demand
                
                # 5. NET REQUIREMENT LOGIC
                avg_daily = f_demand / 7
                if avg_daily == 0: avg_daily = 1
                target_stock = avg_daily * 90 # 90 days Policy
                
                net_req = 0
                if closing < target_stock:
                    net_req = target_stock - closing
                    if p.moq and net_req < p.moq:
                        net_req = p.moq
                    planned = net_req
                    closing = rolling_open + incoming + planned - f_demand
                
                # 6. Status
                dos = closing / avg_daily if avg_daily > 0 else 999
                status = 'OK'
                if dos < 30: status = 'CRITICAL'
                elif dos < 90: status = 'LOW'
                elif dos > 120: status = 'OVERSTOCK'
                
                # 7. Persist
                existing = self.db.query(FactRollingInventory).filter(
                    FactRollingInventory.sku_id == p.sku_id,
                    FactRollingInventory.bucket_date == week_start
                ).first()
                if existing:
                    self.db.delete(existing)
                
                record = FactRollingInventory(
                    sku_id=p.sku_id,
                    bucket_date=week_start,
                    opening_stock=rolling_open,
                    forecast_demand=f_demand,
                    incoming_supply=incoming,
                    planned_supply=planned,
                    closing_stock=closing,
                    min_stock_policy=target_stock,
                    net_requirement=net_req if planned > 0 else 0,
                    status=status
                )
                self.db.add(record)
                
                # C. ROLLOVER
                rolling_open = closing
            
            self.db.commit()
            
        print("Rolling Calculation Complete.")
