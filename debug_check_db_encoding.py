from backend.database import SessionLocal
from backend.models import DimCustomers
import sys
import io

# Force UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_encoding():
    db = SessionLocal()
    try:
        # Get a customer with likely VN characters
        customers = db.query(DimCustomers).limit(10).all()
        for c in customers:
            print(f"Name: {c.customer_name}")
            print(f"Address: {c.address}")
            print("-" * 20)
    finally:
        db.close()

if __name__ == "__main__":
    check_encoding()
