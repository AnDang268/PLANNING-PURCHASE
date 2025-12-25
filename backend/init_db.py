import pyodbc
import os
import re

# Configuration
SERVER = 'localhost'
DATABASE = 'PlanningPurchaseDB'
# Try a list of common Windows drivers
DRIVERS = [
    'ODBC Driver 17 for SQL Server',
    'ODBC Driver 18 for SQL Server',
    'SQL Server',
    'SQL Server Native Client 11.0'
]

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'schema.sql')

def get_connection(db_name='master'):
    for driver in DRIVERS:
        try:
            conn_str = f'DRIVER={{{driver}}};SERVER={SERVER};DATABASE={db_name};Trusted_Connection=yes;TrustServerCertificate=yes;'
            conn = pyodbc.connect(conn_str, autocommit=True)
            print(f"Connected using driver: {driver}")
            return conn
        except Exception as e:
            continue
    print("Could not connect with any known driver. Please ensure ODBC Driver for SQL Server is installed.")
    return None

def init_db():
    print("=== Database Initialization Script ===")
    
    # 1. Create Database if not exists
    conn = get_connection('master')
    if not conn: return
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT name FROM sys.databases WHERE name = N'{DATABASE}'")
        if not cursor.fetchone():
            print(f"Creating database '{DATABASE}'...")
            cursor.execute(f"CREATE DATABASE [{DATABASE}]")
        else:
            print(f"Database '{DATABASE}' already exists.")
    except Exception as e:
        print(f"Error checking/creating DB: {e}")
    finally:
        conn.close()

    # 2. Execute Schema
    print(f"Applying Schema from {SCHEMA_PATH}...")
    conn = get_connection(DATABASE)
    if not conn: return
    cursor = conn.cursor()

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        script = f.read()

    # Split script by 'GO' (case insensitive, on its own line)
    # Regex looks for: Newline -> Optional Whitespace -> GO -> Optional Whitespace -> Newline (or End of String)
    batches = re.split(r'^\s*GO\s*$', script, flags=re.MULTILINE | re.IGNORECASE)

    for i, batch in enumerate(batches):
        clean_batch = batch.strip()
        if not clean_batch: continue
        
        # Remove "USE PlanningPurchaseDB" as we are already connected
        if clean_batch.upper().startswith(f"USE {DATABASE.upper()}"):
            continue

        try:
            cursor.execute(clean_batch)
            print(f"Batch {i+1}: Success")
        except Exception as e:
            # Check if error is "There is already an object..."
            if "There is already an object named" in str(e):
                print(f"Batch {i+1}: Skipped (Already exists)")
            else:
                print(f"Batch {i+1}: ERROR - {e}")

    conn.close()
    print("=== Initialization Complete ===")

if __name__ == "__main__":
    init_db()
