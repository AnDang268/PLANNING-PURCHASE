from backend.database import SessionLocal
from backend.models import PlanningPolicies

db = SessionLocal()
policies = db.query(PlanningPolicies).all()

print(f"Found {len(policies)} policies.")
for p in policies:
    print(f"ID: {p.policy_id}, Name: {p.policy_name}, Days: {p.safety_stock_days}")

if len(policies) == 0:
    print("No policies found. Creating default...")
    default_policy = PlanningPolicies(
        policy_name="Standard Policy",
        safety_stock_days=90,
        service_level_target=0.95,
        is_default=True
    )
    db.add(default_policy)
    db.commit()
    print("Default policy created.")
