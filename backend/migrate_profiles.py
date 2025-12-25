
from backend.database import engine, Base, SessionLocal
from backend.models import PlanningDistributionProfile

def migrate_profiles():
    print("Migrating Planning Profiles Table...")
    Base.metadata.create_all(bind=engine)
    
    # SEED DATA
    db = SessionLocal()
    try:
        profiles = [
            {
                "id": "STD", "name": "Standard (Even Logic)", 
                "desc": "Split Monthly Forecast evenly (25% per week). Best for steady/low-volume items.",
                "ratios": [0.25, 0.25, 0.25, 0.25]
            },
            {
                "id": "B2C", "name": "Retail (Seasonality)", 
                "desc": "High demand in Week 1 (Salary) & Week 4 (Target). Best for Store/Consumer goods.",
                "ratios": [0.35, 0.20, 0.15, 0.30]
            },
            {
                "id": "B2B", "name": "Wholesale (Bulk/Lumpy)", 
                "desc": "Front-loaded demand. 60% in Week 1 (Restock). Best for Bearings/Dealers.",
                "ratios": [0.60, 0.15, 0.15, 0.10]
            }
        ]
        
        for p in profiles:
            existing = db.query(PlanningDistributionProfile).filter_by(profile_id=p["id"]).first()
            if not existing:
                print(f"Seeding Profile: {p['name']}")
                new_profile = PlanningDistributionProfile(
                    profile_id=p["id"],
                    profile_name=p["name"],
                    description=p["desc"],
                    week_1_ratio=p["ratios"][0],
                    week_2_ratio=p["ratios"][1],
                    week_3_ratio=p["ratios"][2],
                    week_4_ratio=p["ratios"][3]
                )
                db.add(new_profile)
            else:
                # Update logic if needed? For now skip
                pass
        
        db.commit()
        print("Seeding Complete.")
        
    except Exception as e:
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_profiles()
