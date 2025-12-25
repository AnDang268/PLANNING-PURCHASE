import sys
import os

# Create absolute path to root and backend
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(current_dir)

from backend.database import SessionLocal, engine
from backend.models import Base, SystemConfig, PlanningPolicies
from datetime import datetime

def init_system_config():
    """
    Initialize System Configuration & Default Parameters from Environment.
    This ensures no hardcoded secrets in the codebase.
    """
    db = SessionLocal()
    try:
        print("Initializing System Configuration...")
        
        # Define default configs or read from Environment
        configs = {
            "MISA_API_URL": os.getenv("MISA_API_URL", "https://crmconnect.misa.vn"),
            "MISA_APP_ID": os.getenv("MISA_APP_ID", "REPLACE_WITH_YOUR_APP_ID"),
            "MISA_ACCESS_TOKEN": os.getenv("MISA_ACCESS_TOKEN", "REPLACE_WITH_YOUR_TOKEN"),
            "LAST_ORDER_SYNC_TIME": os.getenv("LAST_ORDER_SYNC_TIME", "2023-01-01T00:00:00"),
            "LAST_PRODUCT_SYNC_TIME": os.getenv("LAST_PRODUCT_SYNC_TIME", "2023-01-01T00:00:00"),
        }
        
        for key, value in configs.items():
            existing = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
            if existing:
                print(f"Config '{key}' exists. Updating...")
                existing.config_value = value
                existing.updated_at = datetime.now()
            else:
                print(f"Config '{key}' created.")
                new_config = SystemConfig(
                    config_key=key,
                    config_value=value,
                    description=f"Auto-initialized from Environment on {datetime.now()}"
                )
                db.add(new_config)
        
        db.commit()
        print("System Configuration Initialized Successfully!")
        print("NOTE: Please update MISA_APP_ID and MISA_ACCESS_TOKEN in Database or Environment Variables if they are placeholders.")
        
        # --- Initialize Default Planning Parameters ---
        print("\nInitializing Planning Parameters...")
        print("\nInitializing Planning Parameters...")
        
        # Define strict policies for ABC Analysis
        policies = [
            # Class A: High Value/Critical (High Service Level, Low Risk)
            PlanningPolicies(
                policy_name="Class A (High Value)",
                service_level_target=0.98,
                safety_stock_days=30,
                review_period_days=7,  # Review weekly
                forecast_range_days=90,
                lead_time_buffer=5,
                apply_to_category="Electronics", # Example
                is_default=False
            ),
            # Class B: Standard (Balanced)
            PlanningPolicies(
                policy_name="Class B (Standard)",
                service_level_target=0.95,
                safety_stock_days=15,
                review_period_days=30, # Review monthly
                forecast_range_days=90,
                lead_time_buffer=3,
                apply_to_category="Hardware",
                is_default=True
            ),
             # Class C: Low Value (Low Cost, Bulk)
            PlanningPolicies(
                policy_name="Class C (Low Value)",
                service_level_target=0.90,
                safety_stock_days=7,
                review_period_days=90, # Review quarterly
                forecast_range_days=180,
                lead_time_buffer=0,
                apply_to_category="Consumables",
                is_default=False
            )
        ]

        count = 0
        for p in policies:
            existing = db.query(PlanningPolicies).filter(PlanningPolicies.policy_name == p.policy_name).first()
            if not existing:
                db.add(p)
                count += 1
        
        if count > 0:
            db.commit()
            print(f"Created {count} default planning policies (Class A, B, C).")
        else:
            print("Planning Policies already exist. Skipping.")

    except Exception as e:
        print(f"Error initializing config: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_system_config()
