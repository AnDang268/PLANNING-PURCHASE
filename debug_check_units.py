import urllib.request
import json
from backend.database import SessionLocal
from backend.models import DimUnits

def check_db():
    print("--- Database Check ---")
    db = SessionLocal()
    try:
        units = db.query(DimUnits).all()
        print(f"Total Units in DB: {len(units)}")
        for u in units:
            print(f" - {u.unit_id}: {u.unit_name}")
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        db.close()

def check_api():
    print("\n--- API Check ---")
    try:
        with urllib.request.urlopen("http://localhost:8000/api/data/units") as response:
            print(f"Status Code: {response.getcode()}")
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                print(f"Total Units from API: {len(data)}")
                # print(data) 
            else:
                print(f"Error: {response.read()}")
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    check_db()
    check_api()
