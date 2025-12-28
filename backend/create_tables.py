from backend.database import engine, Base
# Import models so they are registered with Base
from backend.models import (
    DimProducts, DimWarehouses, DimVendors, DimProductGroups, 
    FactRollingInventory, FactInventorySnapshots, FactOpeningStock,
    FactPurchases, FactSales, FactForecasts, FactPurchasePlans,
    PlanningPolicies, PlanningDistributionProfile
)

def create_tables():
    print("Connecting to database...")
    print("Creating tables if they do not exist...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    create_tables()
