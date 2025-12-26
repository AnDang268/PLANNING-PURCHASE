import pyodbc
import os
from backend.database import get_connection_string

# Create a test connection
conn_str = get_connection_string().replace('mssql+pyodbc:///?odbc_connect=', '')
# decode URL encoding if needed, but get_connection_string returns sqlalchemy url.
# Let's rebuild raw connection string for pyodbc
server = os.getenv("DB_SERVER", "localhost")
database = os.getenv("DB_DATABASE", "PlanningPurchaseDB")
username = os.getenv("DB_USER", "sa")
password = os.getenv("DB_PASSWORD", "sqlP@ssw0rd")
driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

raw_conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};ChartSet=UTF-8;'

print(f"Connecting to: {server}/{database}...")

try:
    conn = pyodbc.connect(raw_conn_str)
    cursor = conn.cursor()
    
    # Creates a temporary table
    cursor.execute("CREATE TABLE #TestUnicode (id int, text_col NVARCHAR(100))")
    
    # Insert Vietnamese text
    test_text = "Tiếng Việt có dấu: ǎ â ê ô ơ ư"
    cursor.execute("INSERT INTO #TestUnicode VALUES (?, ?)", (1, test_text))
    
    # Read back
    cursor.execute("SELECT text_col FROM #TestUnicode WHERE id = 1")
    row = cursor.fetchone()
    
    print("-" * 30)
    print(f"Original: {test_text}")
    print(f"Stored:   {row[0]}")
    print("-" * 30)
    
    if row[0] == test_text:
        print("✅ DATABASE SUPPORTS UNICODE!")
    else:
        print("❌ DATABASE UNICODE FAILURE!")
        
except Exception as e:
    print(f"Error: {e}")
