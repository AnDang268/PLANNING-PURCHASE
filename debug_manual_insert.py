
from backend.database import SessionLocal
from backend.models import DimCustomers
import uuid

def debug_insert():
    db = SessionLocal()
    try:
        cid = f"TEST_CUST_{uuid.uuid4().hex[:8]}"
        print(f"Inserting {cid}...")
        
        obj = DimCustomers(customer_id=cid, customer_name="Test Persist")
        db.add(obj)
        db.commit()
        
        print("Committed.")
        
        # Verify
        check = db.query(DimCustomers).filter(DimCustomers.customer_id == cid).first()
        if check:
            print(f"Found: {check.customer_name}")
            # Clean up
            # db.delete(check)
            # db.commit()
            print("Persistence Confirmed.")
        else:
            print("NOT FOUND after commit!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_insert()
