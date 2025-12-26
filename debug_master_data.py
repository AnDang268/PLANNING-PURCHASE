
from backend.database import SessionLocal
from backend.models import DimUnits, DimProductGroups

def check_master_data():
    db = SessionLocal()
    try:
        u_count = db.query(DimUnits).count()
        g_count = db.query(DimProductGroups).count()
        
        print("--- Master Data Counts ---")
        print(f"Units: {u_count}")
        print(f"Groups: {g_count}")
        
        if g_count > 0:
            print("\nSample Groups:")
            for g in db.query(DimProductGroups).limit(5).all():
                print(f" - {g.group_id}: {g.group_name}")
                
    finally:
        db.close()

if __name__ == "__main__":
    check_master_data()
