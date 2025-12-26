from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend.models import PlanningDistributionProfile, Base

def seed_profiles():
    db = SessionLocal()
    try:
        # Create tables if not exist (though usually handled by main app)
        PlanningDistributionProfile.__table__.create(bind=engine, checkfirst=True)
        
        profiles = [
            {
                "profile_id": "B2B",
                "profile_name": "Wholesale (Bulk/Lumpy)",
                "description": "Front-loaded demand. 60% in Week 1 (Restock). Best for Bearings/Dealers.",
                "week_1_ratio": 0.60,
                "week_2_ratio": 0.15,
                "week_3_ratio": 0.15,
                "week_4_ratio": 0.10,
                "is_active": True
            },
            {
                "profile_id": "B2C",
                "profile_name": "Retail (Seasonality)",
                "description": "High demand in Week 1 (Salary) & Week 4 (Target). Best for Store/Consumer goods.",
                "week_1_ratio": 0.35,
                "week_2_ratio": 0.20,
                "week_3_ratio": 0.15,
                "week_4_ratio": 0.30,
                "is_active": True
            },
            {
                "profile_id": "STD",
                "profile_name": "Standard (Even Logic)",
                "description": "Split Monthly Forecast evenly (25% per week). Best for steady/low-volume items.",
                "week_1_ratio": 0.25,
                "week_2_ratio": 0.25,
                "week_3_ratio": 0.25,
                "week_4_ratio": 0.25,
                "is_active": True
            }
        ]
        
        for p in profiles:
            existing = db.query(PlanningDistributionProfile).filter_by(profile_id=p["profile_id"]).first()
            if not existing:
                new_profile = PlanningDistributionProfile(**p)
                db.add(new_profile)
                print(f"Created profile: {p['profile_id']}")
            else:
                # Update existing
                existing.profile_name = p["profile_name"]
                existing.description = p["description"]
                existing.week_1_ratio = p["week_1_ratio"]
                existing.week_2_ratio = p["week_2_ratio"]
                existing.week_3_ratio = p["week_3_ratio"]
                existing.week_4_ratio = p["week_4_ratio"]
                print(f"Updated profile: {p['profile_id']}")
        
        db.commit()
        print("Seeding completed successfully.")
        
    except Exception as e:
        print(f"Error seeding profiles: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_profiles()
