from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Date, Text, DECIMAL, CHAR, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.mssql import NVARCHAR
from sqlalchemy.sql import func
from datetime import datetime
from backend.database import Base

class DimUnits(Base):
    __tablename__ = "Dim_Units"
    unit_id = Column(NVARCHAR(50), primary_key=True)
    unit_name = Column(NVARCHAR(100))
    description = Column(NVARCHAR(255))
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class DimProductGroups(Base):
    __tablename__ = "Dim_Product_Groups"
    group_id = Column(NVARCHAR(50), primary_key=True)
    group_name = Column(NVARCHAR(255))
    parent_id = Column(NVARCHAR(50), nullable=True) # For hierarchy
    misa_code = Column(NVARCHAR(50)) # Original Code from MISA
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class DimProducts(Base):
    __tablename__ = "Dim_Products"
    sku_id = Column(NVARCHAR(50), primary_key=True, index=True)
    product_name = Column(NVARCHAR(255))
    
    # New Fields for Master Data
    group_id = Column(NVARCHAR(50), ForeignKey('Dim_Product_Groups.group_id')) # Link to DimProductGroups
    base_unit_id = Column(NVARCHAR(50), ForeignKey('Dim_Units.unit_id')) # Link to DimUnits
    amis_act_id = Column(NVARCHAR(50)) # GUID from AMIS Accounting
    
    # Legacy Fields (Keep for now)
    category = Column(NVARCHAR(100))
    unit = Column(NVARCHAR(50))
    
    min_stock_level = Column(Float, default=0)
    max_stock_level = Column(Float, default=0)
    moq = Column(Float, default=1)          # Minimum Order Quantity
    pack_size = Column(Float, default=1)    # Packaging Specification
    supplier_lead_time_days = Column(Integer, default=7)
    policy_id = Column(Integer, nullable=True) # Linked to Planning Policy
    distribution_profile_id = Column(NVARCHAR(50), ForeignKey('Planning_Distribution_Profiles.profile_id'), nullable=True) # New: Link to Demand Profile (e.g., B2B, B2C)
    abc_class = Column(CHAR(1))
    xyz_class = Column(CHAR(1))
    avg_weekly_sales = Column(Float, default=0) # Imported from Excel Col 5
    is_active = Column(Boolean, default=True) # Added for Planning Optimization
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DimCustomerGroups(Base):
    __tablename__ = "Dim_Customer_Groups"
    group_id = Column(NVARCHAR(50), primary_key=True)
    group_name = Column(NVARCHAR(255))
    parent_id = Column(NVARCHAR(50), nullable=True)
    description = Column(NVARCHAR(255))
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class DimCustomers(Base):
    __tablename__ = "Dim_Customers"
    customer_id = Column(NVARCHAR(50), primary_key=True)
    misa_code = Column(NVARCHAR(100)) # Code displayed in MISA
    customer_name = Column(NVARCHAR(255))
    address = Column(NVARCHAR(500))
    phone = Column(NVARCHAR(100))
    email = Column(NVARCHAR(255))
    group_id = Column(NVARCHAR(50), ForeignKey('Dim_Customer_Groups.group_id')) # FK to DimCustomerGroups
    # Legacy field
    group_name = Column(NVARCHAR(100)) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DimVendors(Base):
    __tablename__ = "Dim_Vendors"
    vendor_id = Column(NVARCHAR(50), primary_key=True)
    vendor_name = Column(NVARCHAR(255))
    contact_person = Column(NVARCHAR(100))
    phone = Column(NVARCHAR(100))
    email = Column(NVARCHAR(255)) # Added email for vendor
    address = Column(NVARCHAR(500)) # Added address for vendor
    tax_code = Column(NVARCHAR(50)) # Added Tax Code
    group_id = Column(NVARCHAR(50), ForeignKey('Dim_Customer_Groups.group_id')) # Potential Vendor Group - Shared with Customer Groups in MISA
    lead_time_avg = Column(Float)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class DimWarehouses(Base):
    __tablename__ = "Dim_Warehouses"
    warehouse_id = Column(NVARCHAR(50), primary_key=True)
    warehouse_code = Column(NVARCHAR(50)) # Added for Excel Mapping (e.g. 66ADV)
    warehouse_name = Column(NVARCHAR(255))
    address = Column(NVARCHAR(500))
    branch_id = Column(NVARCHAR(50))
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class FactSales(Base):
    __tablename__ = "Fact_Sales"
    transaction_id = Column(NVARCHAR(100), primary_key=True)
    order_id = Column(NVARCHAR(50))
    sku_id = Column(NVARCHAR(50), nullable=False)
    order_date = Column(DateTime, nullable=False)
    quantity = Column(Float, nullable=False)
    amount = Column(DECIMAL(18, 2))
    customer_id = Column(NVARCHAR(50))
    is_promotion = Column(Boolean, default=False)
    source = Column(NVARCHAR(20), default='MISA')
    warehouse_id = Column(NVARCHAR(255), default='66 An dương vương') # Added per user request
    extra_data = Column(NVARCHAR, nullable=True) # JSON store for unmapped columns

class FactPurchases(Base):
    __tablename__ = "Fact_Purchases"
    transaction_id = Column(NVARCHAR(50), primary_key=True) # Unique ID (e.g. DocNo_SKU)
    sku_id = Column(NVARCHAR(50), ForeignKey("Dim_Products.sku_id"))
    order_date = Column(DateTime)
    quantity = Column(Float)
    purchase_type = Column(NVARCHAR(20)) # 'ACTUAL' (Received) or 'PLANNED' (Confirmed Order/In Transit)
    order_id = Column(NVARCHAR(50)) # Doc No
    vendor_id = Column(NVARCHAR(50), nullable=True)
    source = Column(NVARCHAR(20), default='IMPORT_FILE')
    warehouse_id = Column(NVARCHAR(255), default='66 An dương vương') # Added per user request
    extra_data = Column(NVARCHAR, nullable=True) # JSON store
    created_at = Column(DateTime, default=datetime.utcnow)

class FactInventorySnapshots(Base):
    __tablename__ = "Fact_Inventory_Snapshots"
    snapshot_date = Column(Date, primary_key=True)
    warehouse_id = Column(NVARCHAR(50), primary_key=True, default='ALL')
    sku_id = Column(NVARCHAR(50), primary_key=True)
    quantity_on_hand = Column(Float, nullable=False)
    quantity_on_order = Column(Float, default=0)
    quantity_allocated = Column(Float, default=0)
    unit = Column(NVARCHAR(50))
    notes = Column(NVARCHAR(255))

class FactOpeningStock(Base):
    """
    Dedicated table for Planning Opening Stock Inputs.
    Populated by Manual Import or Edit.
    Acts as the 'Checkpoint' for Rolling Forecast.
    """
    __tablename__ = "Fact_Opening_Stock"
    stock_date = Column(Date, primary_key=True) # The Cycle/Checkpoint Date
    warehouse_id = Column(NVARCHAR(50), primary_key=True, default='ALL')
    sku_id = Column(NVARCHAR(50), primary_key=True)
    quantity = Column(Float, nullable=False)
    quantity_update = Column(Float, nullable=True) # Override value from user
    unit = Column(NVARCHAR(50)) # Added 2024-12-27
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    notes = Column(NVARCHAR(255))

class FactPurchasePlans(Base):
    __tablename__ = "Fact_Purchase_Plans"
    plan_id = Column(Integer, primary_key=True, index=True)
    plan_date = Column(Date, nullable=False)
    sku_id = Column(NVARCHAR(50), nullable=False)
    warehouse_id = Column(NVARCHAR(50), default='ALL')
    vendor_id = Column(NVARCHAR(50))
    forecast_demand = Column(Float, default=0)
    safety_stock_required = Column(Float, default=0)
    current_stock_on_hand = Column(Float, default=0)
    stock_on_order = Column(Float, default=0)
    suggested_quantity = Column(Float, default=0)
    final_quantity = Column(Float)
    unit_price = Column(Float, default=0)      # Added for Spending Analysis
    total_amount = Column(Float, default=0)    # final_quantity * unit_price
    currency = Column(NVARCHAR(10), default='VND') # Added for Spending Analysis
    status = Column(NVARCHAR(20), default='DRAFT')
    notes = Column(NVARCHAR(500))
    created_at = Column(DateTime, default=func.now())

class FactVendorPerformance(Base):
    __tablename__ = "Fact_Vendor_Performance"
    analysis_month = Column(NVARCHAR(7), primary_key=True)
    vendor_id = Column(NVARCHAR(50), primary_key=True)
    total_orders = Column(Integer, default=0)
    avg_lead_time_actual = Column(Float, default=0)
    delay_rate = Column(Float, default=0)
    quality_score = Column(Float)
    updated_at = Column(DateTime, default=func.now())

class PlanningPolicies(Base):
    __tablename__ = "Planning_Policies"
    policy_id = Column(Integer, primary_key=True, index=True)
    policy_name = Column(NVARCHAR(100), nullable=False)
    service_level_target = Column(Float, default=0.95)
    safety_stock_days = Column(Integer, default=15)
    review_period_days = Column(Integer, default=30)
    forecast_range_days = Column(Integer, default=90)
    lead_time_buffer = Column(Integer, default=3)
    apply_to_category = Column(NVARCHAR(100))
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

class FactForecasts(Base):
    __tablename__ = "Fact_Forecasts"
    run_date = Column(Date, primary_key=True)
    sku_id = Column(NVARCHAR(50), primary_key=True)
    forecast_date = Column(Date, primary_key=True)
    quantity_predicted = Column(Float, nullable=False)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    model_used = Column(NVARCHAR(50))

class SystemSyncLogs(Base):
    __tablename__ = "System_Sync_Logs"
    log_id = Column(Integer, primary_key=True, index=True)
    source = Column(NVARCHAR(20), nullable=False)
    action_type = Column(NVARCHAR(50), nullable=False)
    status = Column(NVARCHAR(20), nullable=False)
    records_processed = Column(Integer, default=0)
    error_message = Column(Text)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime)

class SystemConfig(Base):
    __tablename__ = "System_Configs"
    config_key = Column(NVARCHAR(100), primary_key=True)
    config_value = Column(Text)
    description = Column(NVARCHAR(255))
    is_encrypted = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=func.now())

class FactRollingInventory(Base):
    __tablename__ = "Fact_Rolling_Inventory"
    __table_args__ = (
        UniqueConstraint('sku_id', 'warehouse_id', 'bucket_date', 'profile_id', name='uq_rolling_inventory'),
    )
    planning_id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(NVARCHAR(50), default='STD', index=True) # Partition Key
    sku_id = Column(NVARCHAR(50), nullable=False, index=True)
    warehouse_id = Column(NVARCHAR(50), default='ALL', index=True) # Added for Granular Planning
    bucket_date = Column(Date, nullable=False, index=True) # Start of Week/Month
    opening_stock = Column(Float, default=0)
    forecast_demand = Column(Float, default=0)
    incoming_supply = Column(Float, default=0) # Confirmed PO
    planned_supply = Column(Float, default=0)  # User/System Suggestion
    actual_sold_qty = Column(Float, default=0) # Actual Sales from Sales Book
    actual_imported_qty = Column(Float, default=0) # Actual Import from Warehouse/PO
    closing_stock = Column(Float, default=0)
    min_stock_policy = Column(Float, default=0) # Safety Stock Snapshot
    net_requirement = Column(Float, default=0)
    status = Column(NVARCHAR(20), default='OK') # OK, LOW, CRITICAL
    is_manual_opening = Column(Boolean, default=False) # Flag to respect user override
    updated_at = Column(DateTime, default=func.now())

class PlanningDistributionProfile(Base):
    __tablename__ = "Planning_Distribution_Profiles"
    profile_id = Column(NVARCHAR(50), primary_key=True) # e.g. 'STD', 'B2C', 'B2B'
    profile_name = Column(NVARCHAR(100), nullable=False)
    description = Column(NVARCHAR(255))
    # Weekly Ratios (Sum to 1.0)
    week1 = Column(Float, default=0.25)
    week2 = Column(Float, default=0.25)
    week3 = Column(Float, default=0.25)
    week4 = Column(Float, default=0.25)
    is_active = Column(Boolean, default=True)

class SeasonalFactors(Base):
    __tablename__ = "Seasonal_Factors"
    month = Column(Integer, primary_key=True, autoincrement=False) # 1-12
    demand_multiplier = Column(Float, default=1.0)
    supplier_delay_days = Column(Integer, default=0)
    shipping_delay_days = Column(Integer, default=0)
    description = Column(NVARCHAR(255))
