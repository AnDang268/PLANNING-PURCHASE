from backend.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
print("--- TABLE LIST ---")
try:
    rows = db.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")).fetchall()
    for r in rows:
        print(r[0])
except Exception as e:
    print(e)
db.close()
