
import sys
import os

# Create absolute path to root and backend
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(current_dir)

from sqlalchemy import text, inspect
try:
    from backend.database import engine
except ImportError:
    from database import engine

def migrate():
    print("Starting Migration: Inventory Constraints...")
    with engine.connect() as connection:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('Dim_Products')]
        
        # SQL Server Syntax: ALTER TABLE table ADD column type DEFAULT value
        new_columns = {
            "moq": "FLOAT DEFAULT 1",
            "pack_size": "FLOAT DEFAULT 1"
        }
        
        for col_name, col_def in new_columns.items():
            if col_name not in columns:
                print(f"Adding column '{col_name}'...")
                try:
                    stmt = text(f"ALTER TABLE Dim_Products ADD {col_name} {col_def}")
                    connection.execute(stmt)
                    print(f"Column '{col_name}' added successfully.")
                except Exception as e:
                    print(f"Error adding {col_name}: {e}")
            else:
                print(f"Column '{col_name}' already exists. Skipping.")
        
        connection.commit()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
