from backend.database import SessionLocal, engine
from sqlalchemy import text

def migrate_is_active():
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("SELECT COL_LENGTH('Dim_Products', 'is_active')")).scalar()
            if result is None:
                print("Adding 'is_active' column to Dim_Products...")
                conn.execute(text("ALTER TABLE Dim_Products ADD is_active BIT DEFAULT 1 WITH VALUES"))
                conn.commit()
                print("Migration Successful.")
            else:
                print("Column 'is_active' already exists.")
        except Exception as e:
            print(f"Migration Failed: {e}")

if __name__ == "__main__":
    migrate_is_active()
