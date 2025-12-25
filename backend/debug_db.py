
from backend.database import SessionLocal, engine
from backend.models import DimProducts
import sqlalchemy

def test_db():
    print("Testing DB Connection...")
    try:
        db = SessionLocal()
        print("Session created.")
        
        # Test 1: Connection
        print("Connecting...")
        conn = engine.connect()
        print("Connected!")
        conn.close()
        
        # Test 2: Query
        print("Querying DimProducts...")
        products = db.query(DimProducts).limit(1).all()
        print(f"Query Success! Found {len(products)} products.")
        db.close()
        
    except Exception as e:
        print(f"❌ DB Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_db()
