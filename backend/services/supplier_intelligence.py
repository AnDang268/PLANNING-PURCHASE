
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import random
from backend.models import DimVendors, FactVendorPerformance

class SupplierIntelligenceService:
    def __init__(self, db: Session):
        self.db = db

    def generate_mock_performance_data(self):
        """
        Generates mock performance data for all vendors for the last 6 months.
        """
        vendors = self.db.query(DimVendors).all()
        months = []
        
        # Generate last 6 month keys (YYYY-MM)
        current_date = datetime.now()
        for i in range(6):
            d = current_date - timedelta(days=30 * i)
            months.append(d.strftime("%Y-%m"))

        count = 0
        for vendor in vendors:
            # Randomize base performance for this vendor
            base_quality = random.uniform(85, 100)
            base_lead_time = vendor.lead_time_avg or 7
            
            for month in months:
                # Check if exists
                existing = self.db.query(FactVendorPerformance).filter(
                    FactVendorPerformance.vendor_id == vendor.vendor_id,
                    FactVendorPerformance.analysis_month == month
                ).first()
                
                if existing:
                    continue

                # Add some variance per month
                quality_score = min(100, max(50, base_quality + random.uniform(-5, 5)))
                avg_lead_time_actual = max(1, base_lead_time + random.uniform(-2, 3))
                delay_rate = max(0, min(1, (avg_lead_time_actual - base_lead_time) / base_lead_time if base_lead_time > 0 else 0))
                # Normalize delay rate to be somewhat realistic (0% to 30%)
                delay_rate = random.uniform(0, 0.3) if avg_lead_time_actual > base_lead_time else 0

                perf = FactVendorPerformance(
                    analysis_month=month,
                    vendor_id=vendor.vendor_id,
                    total_orders=random.randint(1, 20),
                    avg_lead_time_actual=round(avg_lead_time_actual, 1),
                    delay_rate=round(delay_rate, 2), # 0.15 = 15%
                    quality_score=round(quality_score, 1)
                )
                self.db.add(perf)
                count += 1
        
        self.db.commit()
        return {"status": "success", "records_generated": count}

    def get_vendor_ranking(self):
        """
        Calculates a composite score for vendors based on the latest month's data.
        Score = (Quality * 0.5) + ((1 - DelayRate) * 100 * 0.3) + (VolumeBonus * 0.2)
        """
        # Get latest available month
        latest_month = self.db.query(func.max(FactVendorPerformance.analysis_month)).scalar()
        if not latest_month:
            return []

        results = self.db.query(
            FactVendorPerformance, DimVendors.vendor_name
        ).join(
            DimVendors, FactVendorPerformance.vendor_id == DimVendors.vendor_id
        ).filter(
            FactVendorPerformance.analysis_month == latest_month
        ).all()

        ranking = []
        for perf, vendor_name in results:
            # Composite Score Calculation
            # 1. Quality (0-100)
            score_quality = perf.quality_score or 0
            
            # 2. Reliability (0-100) -> 100 - (DelayRate * 100)
            score_reliability = max(0, 100 - (perf.delay_rate * 100))
            
            # 3. Final Weighted Score
            # Weight: Quality 60%, Reliability 40%
            final_score = (score_quality * 0.6) + (score_reliability * 0.4)

            ranking.append({
                "vendor_id": perf.vendor_id,
                "vendor_name": vendor_name,
                "score": round(final_score, 1),
                "quality": perf.quality_score,
                "delay_rate": perf.delay_rate,
                "lead_time": perf.avg_lead_time_actual,
                "total_orders": perf.total_orders
            })

        # Sort by score desc
        ranking.sort(key=lambda x: x["score"], reverse=True)
        return ranking

    def get_vendor_history(self, vendor_id: str):
        history = self.db.query(FactVendorPerformance).filter(
            FactVendorPerformance.vendor_id == vendor_id
        ).order_by(FactVendorPerformance.analysis_month.asc()).all()
        return history
