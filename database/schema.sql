-- Create Database (Run this separately if DB doesn't exist)
-- CREATE DATABASE PlanningPurchaseDB;
-- GO

USE PlanningPurchaseDB;
GO

-- 1. Dimension: Products
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Dim_Products]') AND type in (N'U'))
BEGIN
CREATE TABLE [dbo].[Dim_Products](
	[sku_id] [varchar](50) NOT NULL,
	[product_name] [nvarchar](255) NULL,
	[category] [nvarchar](100) NULL,
	[unit] [nvarchar](50) NULL,
	[min_stock_level] [float] NULL DEFAULT 0,
	[max_stock_level] [float] NULL DEFAULT 0, -- Added Max Level
	[supplier_lead_time_days] [int] NULL DEFAULT 7,
	[abc_class] [char](1) NULL, -- A, B, C
	[xyz_class] [char](1) NULL, -- X, Y, Z
	[created_at] [datetime] DEFAULT GETDATE(),
	[updated_at] [datetime] DEFAULT GETDATE(),
 CONSTRAINT [PK_Dim_Products] PRIMARY KEY CLUSTERED 
(
	[sku_id] ASC
)
)
END
GO

-- 2. Fact: Sales History (Transaction Data)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Fact_Sales]') AND type in (N'U'))
BEGIN
CREATE TABLE [dbo].[Fact_Sales](
	[transaction_id] [varchar](100) NOT NULL, -- OrderID_ProductID
	[order_id] [varchar](50) NULL,
	[sku_id] [varchar](50) NOT NULL,
	[order_date] [datetime] NOT NULL,
	[quantity] [float] NOT NULL,
	[amount] [decimal](18, 2) NULL,
	[customer_id] [varchar](50) NULL,
	[is_promotion] [bit] DEFAULT 0,
	[source] [varchar](20) DEFAULT 'MISA', -- MISA, EXCEL, PBI
 CONSTRAINT [PK_Fact_Sales] PRIMARY KEY CLUSTERED 
(
	[transaction_id] ASC
)
)
END
GO

-- 3. Fact: Inventory Snapshots (Daily Stock)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Fact_Inventory_Snapshots]') AND type in (N'U'))
BEGIN
CREATE TABLE [dbo].[Fact_Inventory_Snapshots](
	[snapshot_date] [date] NOT NULL,
	[warehouse_id] [varchar](50) NOT NULL DEFAULT 'ALL', -- Added parameters for warehouse specific stock
	[sku_id] [varchar](50) NOT NULL,
	[quantity_on_hand] [float] NOT NULL,
	[quantity_on_order] [float] DEFAULT 0,
	[notes] [nvarchar](255) NULL,
 CONSTRAINT [PK_Fact_Inventory_Snapshots] PRIMARY KEY CLUSTERED 
(
	[snapshot_date] ASC,
	[warehouse_id] ASC,
	[sku_id] ASC
)
)
END
GO

-- 4. Fact: Forecast Results (AI Output)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Fact_Forecasts]') AND type in (N'U'))
BEGIN
CREATE TABLE [dbo].[Fact_Forecasts](
	[run_date] [date] NOT NULL,
	[sku_id] [varchar](50) NOT NULL,
	[forecast_date] [date] NOT NULL,
	[quantity_predicted] [float] NOT NULL,
	[confidence_lower] [float] NULL,
	[confidence_upper] [float] NULL,
	[model_used] [varchar](50) NULL,
 CONSTRAINT [PK_Fact_Forecasts] PRIMARY KEY CLUSTERED 
(
	[run_date] ASC,
	[sku_id] ASC,
	[forecast_date] ASC
)
)
END
GO

-- 5. System: Sync Logs (Tracking)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[System_Sync_Logs]') AND type in (N'U'))
BEGIN
CREATE TABLE [dbo].[System_Sync_Logs](
	[log_id] [int] IDENTITY(1,1) NOT NULL,
	[source] [varchar](20) NOT NULL, -- MISA, EXCEL
	[action_type] [varchar](50) NOT NULL, -- SYNC_ORDERS, SYNC_PRODUCTS
	[status] [varchar](20) NOT NULL, -- SUCCESS, ERROR
	[records_processed] [int] DEFAULT 0,
	[error_message] [nvarchar](max) NULL,
	[start_time] [datetime] DEFAULT GETDATE(),
	[end_time] [datetime] NULL,
 CONSTRAINT [PK_System_Sync_Logs] PRIMARY KEY CLUSTERED 
(
	[log_id] ASC
)
)
END
GO

-- 6. System: Configs (Settings & Connections)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[System_Configs]') AND type in (N'U'))
BEGIN
CREATE TABLE [dbo].[System_Configs](
	[config_key] [varchar](100) NOT NULL, -- E.g., 'MISA_API_URL', 'MISA_ACCESS_TOKEN'
	[config_value] [nvarchar](max) NULL,
	[description] [nvarchar](255) NULL,
	[is_encrypted] [bit] DEFAULT 0,
	[updated_at] [datetime] DEFAULT GETDATE(),
 CONSTRAINT [PK_System_Configs] PRIMARY KEY CLUSTERED 
(
	[config_key] ASC
)
)

-- Insert Default Configs (Template)
IF NOT EXISTS (SELECT * FROM [dbo].[System_Configs] WHERE [config_key] = 'MISA_API_URL')
BEGIN
	INSERT INTO [dbo].[System_Configs] ([config_key], [config_value], [description])
	VALUES 
		('MISA_API_URL', 'https://api.misa.com.vn/v2', 'Base URL for MISA APIs'),
		('MISA_APP_ID', '', 'Application ID for MISA'),
		('MISA_ACCESS_TOKEN', '', 'Current Access Token (Will be refreshed automatically)'),
		('SYNC_INTERVAL_MINUTES', '60', 'Frequency of automated sync')
END
END
END
END
GO

-- 1.1 Dimension: Customers
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Dim_Customers]') AND type in (N'U'))
BEGIN
CREATE TABLE [dbo].[Dim_Customers](
	[customer_id] [varchar](50) NOT NULL,
	[customer_name] [nvarchar](255) NULL,
	[address] [nvarchar](500) NULL,
	[phone] [varchar](20) NULL,
	[email] [varchar](100) NULL,
	[group_name] [nvarchar](100) NULL,
	[created_at] [datetime] DEFAULT GETDATE(),
	[updated_at] [datetime] DEFAULT GETDATE(),
 CONSTRAINT [PK_Dim_Customers] PRIMARY KEY CLUSTERED 
(
	[customer_id] ASC
)
)
END
GO

-- 1.2 Dimension: Vendors
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Dim_Vendors]') AND type in (N'U'))
BEGIN
CREATE TABLE [dbo].[Dim_Vendors](
	[vendor_id] [varchar](50) NOT NULL,
	[vendor_name] [nvarchar](255) NULL,
	[contact_person] [nvarchar](100) NULL,
	[phone] [varchar](20) NULL,
	[lead_time_avg] [float] NULL,
	[updated_at] [datetime] DEFAULT GETDATE(),
 CONSTRAINT [PK_Dim_Vendors] PRIMARY KEY CLUSTERED 
(
	[vendor_id] ASC
)
)
END
GO

-- 1.3 Dimension: Warehouses
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Dim_Warehouses]') AND type in (N'U'))
BEGIN
CREATE TABLE [dbo].[Dim_Warehouses](
	[warehouse_id] [varchar](50) NOT NULL,
	[warehouse_name] [nvarchar](255) NULL,
	[address] [nvarchar](500) NULL,
	[branch_id] [varchar](50) NULL,
	[updated_at] [datetime] DEFAULT GETDATE(),
 CONSTRAINT [PK_Dim_Warehouses] PRIMARY KEY CLUSTERED 
(
	[warehouse_id] ASC
)
)
END
GO

-- 7. ANALYSIS: Purchase Recommendations
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Fact_Purchase_Plans]') AND type in (N'U'))
BEGIN
CREATE TABLE [dbo].[Fact_Purchase_Plans](
	[plan_id] [int] IDENTITY(1,1) NOT NULL,
	[plan_date] [date] NOT NULL, 
	[sku_id] [varchar](50) NOT NULL,
	[warehouse_id] [varchar](50) DEFAULT 'ALL',
	[vendor_id] [varchar](50) NULL, 
	[forecast_demand] [float] DEFAULT 0,
	[safety_stock_required] [float] DEFAULT 0, 
	[current_stock_on_hand] [float] DEFAULT 0, 
	[stock_on_order] [float] DEFAULT 0,
	[suggested_quantity] [float] DEFAULT 0, 
	[final_quantity] [float] NULL, 
	[status] [varchar](20) DEFAULT 'DRAFT', 
	[notes] [nvarchar](500) NULL,
	[created_at] [datetime] DEFAULT GETDATE(),
 CONSTRAINT [PK_Fact_Purchase_Plans] PRIMARY KEY CLUSTERED 
(
	[plan_id] ASC
)
)
END
GO

-- 8. ANALYSIS: Vendor Performance
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Fact_Vendor_Performance]') AND type in (N'U'))
BEGIN
CREATE TABLE [dbo].[Fact_Vendor_Performance](
	[analysis_month] [varchar](7) NOT NULL, 
	[vendor_id] [varchar](50) NOT NULL,
	[total_orders] [int] DEFAULT 0,
	[avg_lead_time_actual] [float] DEFAULT 0, 
	[delay_rate] [float] DEFAULT 0, 
	[quality_score] [float] NULL, 
	[updated_at] [datetime] DEFAULT GETDATE(),
 CONSTRAINT [PK_Fact_Vendor_Performance] PRIMARY KEY CLUSTERED 
(
	[analysis_month] ASC,
	[vendor_id] ASC
)
)
END
GO

-- 9. CONFIG: Planning Policies
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Planning_Policies]') AND type in (N'U'))
BEGIN
CREATE TABLE [dbo].[Planning_Policies](
	[policy_id] [int] IDENTITY(1,1) NOT NULL,
	[policy_name] [nvarchar](100) NOT NULL, 
	[service_level_target] [float] DEFAULT 0.95,
	[safety_stock_days] [int] DEFAULT 15, 
	[review_period_days] [int] DEFAULT 30, 
	[forecast_range_days] [int] DEFAULT 90, 
	[lead_time_buffer] [int] DEFAULT 3, 
	[apply_to_category] [nvarchar](100) NULL, 
	[is_default] [bit] DEFAULT 0,
	[created_at] [datetime] DEFAULT GETDATE(),
 CONSTRAINT [PK_Planning_Policies] PRIMARY KEY CLUSTERED 
(
	[policy_id] ASC
)
)
-- Insert Default Policies
INSERT INTO [dbo].[Planning_Policies] (policy_name, service_level_target, safety_stock_days, is_default)
VALUES (N'Chính sách Tiêu chuẩn (Standard)', 0.95, 15, 1)
END
GO
