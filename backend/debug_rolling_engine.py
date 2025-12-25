
from backend.database import SessionLocal
from backend.services.rolling_calc import RollingPlanningEngine
import traceback

def debug_engine():
    print("Direct Debug: Rolling Engine")
    db = SessionLocal()
    try:
        engine = RollingPlanningEngine(db)
        # Use existing SKU
        engine.run_rolling_calculation(sku_list=['IPHONE-15'], horizon_months=12)
        print("Success!")
    except Exception:
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_engine()
