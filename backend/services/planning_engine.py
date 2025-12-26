
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
import pandas as pd
import math
from datetime import datetime
from backend.models import DimProducts, DimVendors, FactPurchasePlans, FactSales, PlanningPolicies, PlanningDistributionProfile, FactForecasts

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
        Generate Purchase Plans based on Rolling Inventory 'Current' Net Requirement.
        This ensures users see the same suggestion as in the Rolling Matrix.
        """
        # Clear old draft plans
        self.db.query(FactPurchasePlans).filter(FactPurchasePlans.status == 'DRAFT').delete()
        
        products = {p.sku_id: p for p in self.db.query(DimProducts).all()}
        plans_created = 0
        
        from backend.models import FactRollingInventory
        from datetime import date
        
        # 1. Determine Current Rolling Bucket Date
        today = date.today()
        # Logic: 1-7 -> 1; 8-14 -> 8; 15-21 -> 15; 22+ -> 22
        day = today.day
        bucket_day = 1
        if day >= 22: bucket_day = 22
        elif day >= 15: bucket_day = 15
        elif day >= 8: bucket_day = 8
        
        current_bucket_date = date(today.year, today.month, bucket_day)
        
        print(f"Generating Plans for Bucket: {current_bucket_date}")
        
        # 2. Query Rolling Inventory for Needs
        requirements = self.db.query(FactRollingInventory).filter(
            FactRollingInventory.bucket_date == current_bucket_date,
            FactRollingInventory.net_requirement > 0
        ).all()
        
        for req in requirements:
            product = products.get(req.sku_id)
            if not product: continue
            
            final_qty = req.net_requirement
            
            # Apply Pack Size Constraint (Round up) - MOQ already applied in Rolling Calc?
            # Double check MOQ just in case
            if product.moq and final_qty < product.moq:
                final_qty = product.moq
            
            pack_size = product.pack_size or 1
            if pack_size > 1:
                remainder = final_qty % pack_size
                if remainder > 0:
                    final_qty += (pack_size - remainder)
            
            # Create Plan
            plan = FactPurchasePlans(
                plan_date=today,
                sku_id=req.sku_id,
                vendor_id=None, # To be assigned
                forecast_demand=req.forecast_demand, 
                safety_stock_required=req.min_stock_policy,
                suggested_quantity=req.net_requirement, # Raw need
                final_quantity=final_qty, # Constrained need
                total_amount=0, 
                currency='VND',
                status='DRAFT',
                notes=f"Generated from Rolling Calc (Bucket {current_bucket_date})"
            )
            self.db.add(plan)
            plans_created += 1
            
        self.db.commit()
        return {"status": "success", "plans_generated": plans_created, "bucket_date": str(current_bucket_date)}

    def update_plan(self, plan_id: int, final_quantity: float, status: str = None, notes: str = None):
        plan = self.db.query(FactPurchasePlans).filter(FactPurchasePlans.plan_id == plan_id).first()
        if not plan:
            raise Exception("Plan not found")
        
        # Only allow updates if not already approved/ordered (unless admin override, but let's keep simple)
        if plan.status == 'APPROVED':
             raise Exception("Cannot update an approved plan")

        plan.final_quantity = final_quantity
        if status:
            plan.status = status
        if notes:
            plan.notes = notes
            
        self.db.commit()
        return {"status": "success", "message": "Plan updated"}

    def approve_plan(self, plan_id: int):
        plan = self.db.query(FactPurchasePlans).filter(FactPurchasePlans.plan_id == plan_id).first()
        if not plan:
            raise Exception("Plan not found")
            
        plan.status = 'APPROVED'
        # In a real system, this might trigger an Email or create a PO record
        
        self.db.commit()
        return {"status": "success", "message": "Plan approved"}

    def delete_plan(self, plan_id: int):
        plan = self.db.query(FactPurchasePlans).filter(FactPurchasePlans.plan_id == plan_id).first()
        if not plan:
            raise Exception("Plan not found")
            
        if plan.status == 'APPROVED':
             raise Exception("Cannot delete an approved plan")

        self.db.delete(plan)
        self.db.commit()
        return {"status": "success", "message": "Plan deleted"}

    def delete_plan(self, plan_id: int):
        plan = self.db.query(FactPurchasePlans).filter(FactPurchasePlans.plan_id == plan_id).first()
        if not plan:
            raise Exception("Plan not found")
            
        if plan.status == 'APPROVED':
             raise Exception("Cannot delete an approved plan")

        self.db.delete(plan)
        self.db.commit()
        return {"status": "success", "message": "Plan deleted"}

    def get_rolling_inventory_matrix(self, limit: int = 100, search: str = None, group_id: str = None, warehouse_id: str = None):
        """
        Fetch Rolling Inventory Data and pivot it for the UI Matrix.
        Structure:
        [
            {
                "sku_id": "SKU1",
                "product_name": "Product 1",
                ...
                "weeks": {
                    "2023-11-01": { opening: 10, closing: 5, ... },
                    "2023-11-08": { ... }
                }
            }
        ]
        """
        from backend.models import FactRollingInventory, DimProductGroups
        
        query = self.db.query(
            FactRollingInventory, 
            DimProducts.product_name, 
            DimProducts.category,
            DimProductGroups.group_name
        ).join(
            DimProducts, FactRollingInventory.sku_id == DimProducts.sku_id
        ).outerjoin(
            DimProductGroups, DimProducts.group_id == DimProductGroups.group_id
        )

        if search:
            query = query.filter(FactRollingInventory.sku_id.ilike(f"%{search}%"))
            
        if group_id and group_id != "ALL":
            query = query.filter(DimProducts.group_id == group_id)
            
        # Warehouse Filter
        if warehouse_id and warehouse_id != "ALL":
            query = query.filter(FactRollingInventory.warehouse_id == warehouse_id)
        else:
            # If no specific warehouse is selected, we should conceptually SUM.
            # However, for simplicity now, let's just filter for 'ALL' records if our Import logic created them?
            # Or if Import created specific warehouses, we need to show them.
            # Ideally, the Matrix shows "Global View" by default.
            # If the user imported separate warehouses, we either SUM them or show 'ALL' entries.
            # Let's assume for now user plans on 'ALL' or specific.
            # If we don't filter, we get duplicates.
            # Let's default to prioritizing 'ALL' entries if they exist, or fetch all and aggregate in python loop.
            # BETTER APPROACH: Just filter 'ALL' by default if no warehouse specified?
            # But the user imported '66ADV'. 
            # So let's aggregate in Python if no warehouse filtered.
            pass

        # Get raw data
        # Note: Parsing 1000s of rows might be slow without proper SQL Pivot, 
        # but for this scale (client-side pivoting) it's acceptable.
        results = query.order_by(FactRollingInventory.sku_id, FactRollingInventory.bucket_date).limit(limit * 10).all() 
        # Increased limit to handle warehouse multiplicity
        
        # Transform to Matrix
        matrix = {}
        
        for row in results:
            item = row[0] # FactRollingInventory
            p_name = row[1]
            cat = row[2]
            g_name = row[3]
            
            # If filtering by warehouse, exact match is done by SQL.
            # If NOT filtering (Global View), we need to Aggregate.
            # Unique Key for aggregation: SKU + Date
            
            if item.sku_id not in matrix:
                matrix[item.sku_id] = {
                    "sku_id": item.sku_id,
                    "product_name": p_name or "",
                    "category": cat or "",
                    "group_name": g_name or "",
                    "weeks": {}
                }
            
            date_key = item.bucket_date.isoformat()
            
            if date_key not in matrix[item.sku_id]["weeks"]:
                 matrix[item.sku_id]["weeks"][date_key] = {
                    "sku_id": item.sku_id,
                    "product_name": p_name,
                    "category": cat,
                    "bucket_date": date_key,
                    "opening_stock": 0,
                    "forecast": 0,
                    "incoming": 0,
                    "planned": 0,
                    "closing": 0,
                    "status": "OK",
                    "net_req": 0,
                    "dos": 0
                 }
            
            # Aggregate or Set
            entry = matrix[item.sku_id]["weeks"][date_key]
            entry["opening_stock"] += item.opening_stock or 0
            entry["forecast"] += item.forecast_demand or 0
            entry["incoming"] += item.incoming_supply or 0
            entry["planned"] += item.planned_supply or 0
            entry["closing"] += item.closing_stock or 0
            entry["net_req"] += item.net_requirement or 0
            
            # Status logic (simple override for now, e.g. if any is LOW)
            if item.status == 'LOW' or item.status == 'CRITICAL':
                 entry["status"] = item.status

            
        return list(matrix.values())
