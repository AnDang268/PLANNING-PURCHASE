
from backend.database import SessionLocal, engine
from sqlalchemy import text

def test_raw_update():
    db = SessionLocal()
    try:
        # Target ID
        target_id = "BTH.AnhTran"
        
        # Raw SQL update
        sql = text("UPDATE Dim_Customers SET customer_name = :name WHERE customer_id = :id")
        
        correct_name = "CH Anh Trân - Phan Rí"
        print(f"Updating Raw to: {correct_name}")
        
        db.execute(sql, {"name": correct_name, "id": target_id})
        db.commit()
        
        # Read back passing normal ORM
        # But maybe raw read is safer
        result = db.execute(text("SELECT customer_name FROM Dim_Customers WHERE customer_id = :id"), {"id": target_id}).fetchone()
        print(f"Read Back Raw: {result[0]}")
        
        if result[0] == correct_name:
             print("SUCCESS: Raw Update Worked.")
        else:
             print("FAIL: Raw Update Failed.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_raw_update()
