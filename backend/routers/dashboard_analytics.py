from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any

from backend.database import get_db
from backend.models import FactPurchasePlans, DimProducts, DimVendors

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)

@router.get("/spending")
def get_spending_analytics(db: Session = Depends(get_db)):
    """
    Get spending analytics for Purchasing Intelligence Dashboard.
    Returns:
        - Total Spend (Planned)
        - Active Plans Count
        - Spend by Category
        - Spend by Vendor
    """
    
    # 1. Total Spend (Status = APPROVED or PLANNED/DRAFT depending on logic, taking ALL for now or specific status)
    # Assuming analysis on 'APPROVED' plans represents committed spend, but for planning insight we might look at all non-cancelled.
    total_spend_query = db.query(
        func.sum(FactPurchasePlans.total_amount)
    ).filter(FactPurchasePlans.status != 'CANCELLED')
    
    total_spend = total_spend_query.scalar() or 0
    
    # 2. Total Plans
    total_plans = db.query(FactPurchasePlans).count()
    
    # 3. Spend by Category
    # Join with DimProducts to get category
    spend_by_category = db.query(
        DimProducts.category,
        func.sum(FactPurchasePlans.total_amount).label("total")
    ).join(DimProducts, FactPurchasePlans.sku_id == DimProducts.sku_id)\
     .group_by(DimProducts.category)\
     .order_by(desc("total"))\
     .limit(10).all()
     
    # 4. Spend by Vendor
    # Join with DimVendors
    spend_by_vendor = db.query(
        DimVendors.vendor_name,
        func.sum(FactPurchasePlans.total_amount).label("total")
    ).join(DimVendors, FactPurchasePlans.vendor_id == DimVendors.vendor_id)\
     .group_by(DimVendors.vendor_name)\
     .order_by(desc("total"))\
     .limit(10).all()

    return {
        "status": "success",
        "data": {
            "kpi": {
                "total_spend": total_spend,
                "total_plans": total_plans,
                "currency": "VND"
            },
            "charts": {
                "spend_by_category": [
                    {"name": cat, "value": val} for cat, val in spend_by_category
                ],
                "spend_by_vendor": [
                    {"name": vend, "value": val} for vend, val in spend_by_vendor
                ]
            }
        }
    }

@router.get("/recent-activity")
def get_recent_activity(db: Session = Depends(get_db)):
    """
    Get 5 most recent purchase plans for dashboard activity feed.
    """
    recent_plans = db.query(
        FactPurchasePlans.plan_id,
        FactPurchasePlans.sku_id,
        FactPurchasePlans.status,
        FactPurchasePlans.total_amount,
        FactPurchasePlans.created_at,
        FactPurchasePlans.currency
    ).order_by(desc(FactPurchasePlans.created_at)).limit(5).all()

    return {
        "status": "success",
        "data": [
            {
                "id": str(p.plan_id),
                "sku_id": p.sku_id,
                "order_id": f"PLAN-{p.plan_id}", # Synthetic Order ID
                "status": p.status,
                "amount": p.total_amount,
                "currency": p.currency,
                "date": p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else None
            }
            for p in recent_plans
        ]
    }
