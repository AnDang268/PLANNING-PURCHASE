
from backend.database import SessionLocal
from backend.models import DimCustomers

def test_manual_update():
    db = SessionLocal()
    try:
        # Target: CH Anh TrÃ¢n - Phan RÃ­ (ID: BTH.AnhTran)
        target_id = "BTH.AnhTran"
        
        obj = db.query(DimCustomers).filter(DimCustomers.customer_id == target_id).first()
        if not obj:
            print(f"Customer {target_id} not found.")
            return

        print(f"Current Name: {obj.customer_name}")
        
        # Force Update to Correct Name
        correct_name = "CH Anh Trân - Phan Rí"
        print(f"Updating to: {correct_name}")
        
        obj.customer_name = correct_name
        db.commit()
        db.refresh(obj)
        
        print(f"Read Back:   {obj.customer_name}")
        
        if obj.customer_name == correct_name:
             print("SUCCESS: Manual Update Worked.")
        else:
             print("FAIL: Manual Update Failed.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_manual_update()
