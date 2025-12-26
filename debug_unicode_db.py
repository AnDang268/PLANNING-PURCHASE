from backend.database import SessionLocal, engine
from backend.models import DimUnits
from sqlalchemy import text
import uuid

def test_unicode():
    db = SessionLocal()
    try:
        # 1. Create a Test Unit with Unicode
        test_id = f"TEST-{uuid.uuid4().hex[:8]}"
        test_name = "Unit Cặp Đôi (Test)"
        print(f"Inserting: {test_name}")
        
        unit = DimUnits(unit_id=test_id, unit_name=test_name)
        db.add(unit)
        db.commit()
        
        # 2. Read it back
        saved_unit = db.query(DimUnits).filter(DimUnits.unit_id == test_id).first()
        print(f"Read Back: {saved_unit.unit_name}")
        
        if saved_unit.unit_name == test_name:
            print("SUCCESS: Database handles Unicode correctly.")
        else:
            print(f"FAILURE: Database returned '{saved_unit.unit_name}' instead of '{test_name}'")
            
        # Cleanup
        db.delete(saved_unit)
        db.commit()
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_unicode()
