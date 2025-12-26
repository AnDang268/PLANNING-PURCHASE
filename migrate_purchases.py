
import pyodbc

# Hardcoded connection string for direct migration
conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=PlanningPurchaseDB;Trusted_Connection=yes;"

def migrate():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("Creating Fact_Purchases table...")
        
        sql = """
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Fact_Purchases]') AND type in (N'U'))
        BEGIN
            CREATE TABLE [dbo].[Fact_Purchases](
                [transaction_id] [nvarchar](50) NOT NULL,
                [sku_id] [nvarchar](50) NULL,
                [order_date] [datetime] NULL,
                [quantity] [float] NULL,
                [purchase_type] [nvarchar](20) NULL,
                [order_id] [nvarchar](50) NULL,
                [vendor_id] [nvarchar](50) NULL,
                [source] [nvarchar](20) NULL,
                [extra_data] [nvarchar](max) NULL,
                [created_at] [datetime] DEFAULT GETDATE(),
                PRIMARY KEY CLUSTERED ([transaction_id] ASC)
            )
        END
        """
        cursor.execute(sql)
        conn.commit()
        print("Success.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    migrate()
