import pyodbc
from init_db import get_connection, DATABASE

def check_tables():
    conn = get_connection(DATABASE)
    if not conn: return
    cursor = conn.cursor()
    
    print(f"Checking tables in {DATABASE}...")
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'")
    tables = [row.table_name for row in cursor.fetchall()]
    
    expected_tables = [
        'Dim_Products', 'Dim_Customers', 'Dim_Vendors', 'Dim_Warehouses',
        'Fact_Sales', 'Fact_Inventory_Snapshots', 'Fact_Forecasts',
        'Fact_Purchase_Plans', 'Fact_Vendor_Performance',
        'System_Sync_Logs', 'System_Configs', 'Planning_Policies'
    ]
    
    missing = []
    for t in expected_tables:
        if t in tables:
            print(f"[OK] {t}")
        else:
            print(f"[MISSING] {t}")
            missing.append(t)
            
    conn.close()

if __name__ == "__main__":
    check_tables()
