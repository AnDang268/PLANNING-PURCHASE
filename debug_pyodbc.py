import pyodbc
import os

def test_pyodbc():
    server = os.getenv("DB_SERVER", "localhost")
    database = os.getenv("DB_DATABASE", "PlanningPurchaseDB")
    username = os.getenv("DB_USER", "sa")
    password = os.getenv("DB_PASSWORD", "sqlP@ssw0rd")
    driver = "ODBC Driver 17 for SQL Server"
    
    conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};'
    
    print(f"Connecting with: {conn_str}")
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        test_sku = "TEST-PYODBC"
        test_name = "Chữ Việt Có Dấu"
        
        # Cleanup
        cursor.execute("DELETE FROM Dim_Products WHERE sku_id = ?", test_sku)
        
        # Insert
        print(f"Inserting: {test_name}")
        cursor.execute("INSERT INTO Dim_Products (sku_id, product_name) VALUES (?, ?)", test_sku, test_name)
        conn.commit()
        
        # Read
        cursor.execute("SELECT product_name FROM Dim_Products WHERE sku_id = ?", test_sku)
        row = cursor.fetchone()
        
        if row:
            print(f"Read Back: {row[0]}")
            if row[0] == test_name:
                print("SUCCESS: PyODBC handles Unicode correctly.")
            else:
                print("FAILURE: Unicode mismatch.")
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_pyodbc()
