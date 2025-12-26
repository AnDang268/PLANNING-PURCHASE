from backend.database import engine
from sqlalchemy import text, inspect
from backend.models import DimProducts, DimVendors, FactPurchasePlans

def check_schema():
    inspector = inspect(engine)
    
    models = [
        ('Dim_Products', DimProducts),
        ('Dim_Vendors', DimVendors),
        ('Fact_Purchase_Plans', FactPurchasePlans)
    ]
    
    with engine.connect() as conn:
        for table_name, model in models:
            print(f"Checking table: {table_name}")
            # Get existing columns in DB
            columns_in_db = [c['name'] for c in inspector.get_columns(table_name)]
            
            # Get columns in SQLAlchemy Model
            # Mapper.columns returns Column objects
            model_columns = [c.name for c in model.__table__.columns]
            
            missing = set(model_columns) - set(columns_in_db)
            
            if missing:
                print(f"!! MISSING COLUMNS in {table_name}: {missing}")
                # Attempt Fix
                for col in missing:
                    print(f"  -> Adding {col}...")
                    # Determine type (simple Mapping)
                    # This is a bit hacky, but works for MVP fix
                    col_obj = model.__table__.columns[col]
                    col_type = col_obj.type.compile(engine.dialect)
                    
                    try:
                        alter_sql = f"ALTER TABLE {table_name} ADD {col} {col_type} NULL"
                        conn.execute(text(alter_sql))
                        print(f"     Added {col}.")
                    except Exception as e:
                        print(f"     Failed to add {col}: {e}")
                conn.commit()
            else:
                print(f"OK: {table_name}")

if __name__ == "__main__":
    check_schema()
