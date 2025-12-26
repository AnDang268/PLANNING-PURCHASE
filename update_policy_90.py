from backend.database import SessionLocal
from backend.models import PlanningPolicies

db = SessionLocal()
policy = db.query(PlanningPolicies).filter_by(is_default=True).first()
if not policy:
    policy = db.query(PlanningPolicies).first()

if policy:
    print(f"Updating policy '{policy.policy_name}' from {policy.safety_stock_days} to 90 days.")
    policy.safety_stock_days = 90
    db.commit()
    print("Update complete.")
else:
    print("No policy found to update.")
