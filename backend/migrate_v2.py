import sys
from sqlalchemy import create_engine, text
from sqlalchemy.engine import reflection

# Database connection setup
# Assuming standard SQLite for development or connecting to connection string in database.py
# For now, importing from database.py to reuse connection logic
try:
    from database import engine
except ImportError:
    # Fallback/Standalone execution if run from root
    from backend.database import engine

def migrate():
    print("Starting migration v2...")
    with engine.connect() as connection:
        # Check if columns exist
        inspector = reflection.Inspector.from_engine(engine)
        columns = [col['name'] for col in inspector.get_columns('Fact_Purchase_Plans')]
        
        new_columns = {
            "unit_price": "FLOAT DEFAULT 0",
            "total_amount": "FLOAT DEFAULT 0",
            "currency": "VARCHAR(10) DEFAULT 'VND'"
        }
        
        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                print(f"Adding column '{col_name}'...")
                alter_stmt = text(f"ALTER TABLE Fact_Purchase_Plans ADD COLUMN {col_name} {col_type}")
                connection.execute(alter_stmt)
                print(f"Column '{col_name}' added.")
            else:
                print(f"Column '{col_name}' already exists. Skipping.")
        
        connection.commit()
    print("Migration v2 completed.")

if __name__ == "__main__":
    migrate()
