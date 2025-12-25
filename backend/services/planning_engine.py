
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
import pandas as pd
import math
from datetime import datetime
from backend.models import DimProducts, DimVendors, FactPurchasePlans, FactSales, PlanningPolicies

class PlanningEngine:
    def __init__(self, db: Session):
        self.db = db
        # Cache policies for performance
        self.policies = {p.policy_name: p for p in self.db.query(PlanningPolicies).all()}

    def _get_policy_param(self, policy_name: str, param: str, default: float) -> float:
        """Helper to get policy parameter or return default."""
        policy = self.policies.get(policy_name)
        if policy and hasattr(policy, param):
            return getattr(policy, param)
        return default

    def calculate_safety_stock(self):
        """
        Calculate Dynamic Safety Stock using the formula:
        SS = Z * StdDev_Demand * Sqrt(Avg_Lead_Time)
        
        Where:
        - Z: Service Level Factor (e.g., 1.65 for 95%)
        - StdDev_Demand: Standard Deviation of daily sales over the review period.
        - Avg_Lead_Time: From DimVendors (or DimProducts if specific).
        """
        products = self.db.query(DimProducts).all()
        updated_count = 0
        
        # Default Z-factor for 95% Service Level
        # In a real system, this would map from the 'service_level' column (e.g. 0.95 -> 1.65)
        Z_FACTOR = 1.65 

        for product in products:
            # 1. Get Sales History (last 90 days)
            sales_data = self.db.query(FactSales.quantity).filter(
                FactSales.sku_id == product.sku_id
            ).all()
            
            quantities = [s[0] for s in sales_data]
            
            if len(quantities) < 5: 
                # Not enough data points for reliable StdDev, skip or use static
                continue
            
            # 2. Calculate Standard Deviation
            std_dev = pd.Series(quantities).std()
            if pd.isna(std_dev):
                std_dev = 0
                
            # 3. Get Lead Time (Default 7 days if not set)
            long_lead_time = product.supplier_lead_time_days or 7
            
            # 4. Calculate Safety Stock
            # Formula: SS = Z * StdDev * Sqrt(LT)
            safety_stock = Z_FACTOR * std_dev * math.sqrt(long_lead_time)
            
            # 5. Update Product
            product.min_stock_level = round(safety_stock, 2)
            updated_count += 1
            
        self.db.commit()
        return {"status": "success", "updated_products": updated_count}

    def generate_purchase_plans(self):
        """
        Generate Purchase Plans based on Net Requirement:
        Net_Req = (Safety_Stock + Cycle_Stock) - (Current_Stock + In_Transit)
        """
        # Clear old draft plans
        self.db.query(FactPurchasePlans).filter(FactPurchasePlans.status == 'DRAFT').delete()
        
        products = self.db.query(DimProducts).all()
        plans_created = 0
        
        for product in products:
            # Simple assumption: Cycle Stock = Demand * Lead Time (Pipeline Inventory)
            # For this MVP, we will simplify: NetReq = MinStock (Safety) - CurrentStock(assumed 0 for now as we don't have inventory table)
            # TODO: Integrate real Inventory Snapshot table.
            
            # In absence of generic inventory table, let's assume 'min_stock_level' IS the target we must maintain.
            # And let's assume current stock is 0 (worst case) for generation if not tracked.
            # OR we can mock it.
            
            # For a realistic MVP, let's calculate simplistic Net Req
            # NetReq = Target(MinStock) - Current(0)
            net_req = product.min_stock_level
            
            if net_req <= 0:
                continue
                
            # --- APPLY CONSTRAINTS ---
            
            # 1. MOQ Constraint
            final_qty = max(net_req, product.moq or 1)
            
            # 2. Pack Size Constraint (Round up to nearest multiple)
            pack_size = product.pack_size or 1
            if pack_size > 1:
                remainder = final_qty % pack_size
                if remainder > 0:
                    final_qty += (pack_size - remainder)
            
            # Create Plan
            plan = FactPurchasePlans(
                plan_date=datetime.now(),
                sku_id=product.sku_id,
                vendor_id=None, # To be assigned
                suggested_quantity=net_req,
                final_quantity=final_qty,
                total_amount=0, # Need price
                currency='VND',
                status='DRAFT'
            )
            self.db.add(plan)
            plans_created += 1
            
        self.db.commit()
        return {"status": "success", "plans_generated": plans_created}
