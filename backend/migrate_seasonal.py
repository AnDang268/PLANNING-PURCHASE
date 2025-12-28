from backend.database import engine
from backend.models import SeasonalFactors
from sqlalchemy import text

def apply_migration():
    print("Re-creating Seasonal_Factors table...")
    
    defaults = [
        {"m":1, "d":1.00, "sd":0, "shd":0, "desc":'Normal'},
        {"m":2, "d":1.00, "sd":25, "shd":0, "desc":'Tet - NCC Nghi 25 ngay'},
        {"m":3, "d":1.25, "sd":0, "shd":0, "desc":'Mua nong nghiep bat dau'},
        {"m":4, "d":1.25, "sd":0, "shd":0, "desc":'Mua nong nghiep'},
        {"m":5, "d":1.25, "sd":0, "shd":0, "desc":'Mua nong nghiep'},
        {"m":6, "d":1.00, "sd":0, "shd":7, "desc":'Ket tau'},
        {"m":7, "d":1.00, "sd":8, "shd":7, "desc":'Thoi tiet nong + Ket tau'},
        {"m":8, "d":1.00, "sd":8, "shd":0, "desc":'Thoi tiet nong'},
        {"m":9, "d":1.30, "sd":0, "shd":0, "desc":'Mua thu dong bat dau'},
        {"m":10, "d":1.30, "sd":10, "shd":0, "desc":'Cao diem NCC'},
        {"m":11, "d":1.30, "sd":12, "shd":10, "desc":'Cao diem + Lanh + Ket tau'},
        {"m":12, "d":1.35, "sd":12, "shd":10, "desc":'Peak - Du tru Tet'}
    ]

    with engine.connect() as conn:
        try:
            print("Dropping existing table...")
            conn.execute(text("DROP TABLE IF EXISTS Seasonal_Factors"))
            conn.commit()
        except Exception as e:
            print(f"Drop failed (might not exist): {e}")

        print("Creating table...")
        SeasonalFactors.__table__.create(bind=engine)
        
        print("Seeding default seasonal data...")
        stmt = text("INSERT INTO Seasonal_Factors (month, demand_multiplier, supplier_delay_days, shipping_delay_days, description) VALUES (:m, :d, :sd, :shd, :desc)")
        
        for row in defaults:
            try:
                conn.execute(stmt, row)
            except Exception as e:
                 print(f"Failed to insert row {row['m']}: {e}")
        
        conn.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    apply_migration()
