from backend.database import engine
from sqlalchemy import text

def force_create_table():
    print("Forcing creation of Fact_Opening_Stock...")
    
    sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Fact_Opening_Stock' AND xtype='U')
    BEGIN
        CREATE TABLE Fact_Opening_Stock (
            stock_date DATE NOT NULL,
            warehouse_id NVARCHAR(50) NOT NULL DEFAULT 'ALL',
            sku_id NVARCHAR(50) NOT NULL,
            quantity FLOAT NOT NULL,
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE(),
            notes NVARCHAR(255),
            PRIMARY KEY (stock_date, warehouse_id, sku_id)
        );
        PRINT 'Table Fact_Opening_Stock created successfully.';
    END
    ELSE
    BEGIN
        PRINT 'Table Fact_Opening_Stock already exists.';
    END
    """
    
    try:
        with engine.connect() as connection:
            connection.execute(text(sql))
            connection.commit()
            print("SQL Execution Completed.")
            
            # Verify
            result = connection.execute(text("SELECT TOP 1 * FROM Fact_Opening_Stock"))
            print("Verification Select executed (Empty Result is OK).")
            
    except Exception as e:
        print(f"Error creating table: {e}")

if __name__ == "__main__":
    force_create_table()
