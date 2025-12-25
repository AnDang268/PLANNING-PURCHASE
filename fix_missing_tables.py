from backend.database import engine, Base
# Must import ALL models so Base knows about them
from backend.models import (
    DimUnits, DimProductGroups, DimCustomerGroups, DimWarehouses,
    DimProducts, DimCustomers, DimVendors,
    FactSales, FactPurchasePlans, FactInventorySnapshots, 
    FactVendorPerformance, FactForecasts, FactRollingInventory,
    PlanningPolicies, PlanningDistributionProfile,
    SystemSyncLogs, SystemConfig
)
from sqlalchemy import inspect

print("--- FIXING MISSING TABLES ---")
# 1. Create All Tables (Safe: checkfirst=True is default)
print("Creating tables if not exist...")
Base.metadata.create_all(bind=engine)

# 2. Verify
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Current Tables: {tables}")

MISSING = ["Dim_Units", "Dim_Product_Groups", "Dim_Customer_Groups"]
for t in MISSING:
    if t in tables:
        print(f"[OK] {t} exists.")
    else:
        print(f"[FAIL] {t} still missing!")
