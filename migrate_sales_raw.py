
import pyodbc

# Hardcoded connection string for direct migration (bypass SQLAlchemy weirdness)
conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=PlanningPurchaseDB;Trusted_Connection=yes;"

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Adding extra_data to Fact_Sales...")
    # SQL Server specific syntax
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Fact_Sales') AND name = 'extra_data') BEGIN ALTER TABLE Fact_Sales ADD extra_data NVARCHAR(MAX); END")
    conn.commit()
    print("Success.")
except Exception as e:
    print(f"Error: {e}")
