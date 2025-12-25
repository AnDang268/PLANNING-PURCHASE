import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine

def check_counts():
    print(">>> Checking Table Counts...")
    with engine.connect() as conn:
        tables = ['Dim_Products', 'Dim_Units', 'Dim_Product_Groups', 'Dim_Customers', 'Dim_Vendors']
        for t in tables:
            try:
                res = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
                print(f"{t}: {res}")
            except Exception as e:
                print(f"{t}: ERROR {e}")

if __name__ == "__main__":
    check_counts()
