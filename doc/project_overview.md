# Project Overview

## Intelligent Demand Planning & Inventory Optimization System

### 1. Goal
The goal of this project is to build an intelligent system that integrates with MISA AMIS CRM/ERP to optimize purchasing and inventory management. It leverages AI/Machine Learning to forecast sales demand, calculate safety stock dynamically, and recommend purchase orders to maintain optimal inventory levels.

### 2. Purpose
- **Automate Purchasing**: Replace manual Excel-based planning with data-driven recommendations.
- **Optimize Inventory**: Reduce stockouts (lost sales) and overstock (frozen capital) using AI forecasting.
- **Integration**: seamless sync with MISA AMIS for products, orders, and inventory data.
- **Visualization**: Provide a clear, Excel-like interface for planning managers to review and approve purchase plans.

### 3. Key Features
- **Data Synchronization**: Auto-fetch Products, Sales Orders, and Customers from MISA AMIS.
- **AI Forecasting**: Predict future demand using statistical (Croston, ARIMA) and ML (XGBoost) models.
- **Inventory Analysis**: Calculate Safety Stock, Reorder Points, and Economic Order Quantity (EOQ).
- **Purchase Planning**: Generate purchasing plans based on lead times and vendor performance.
- **Rolling Forecast**: View 12-month rolling sales and inventory projections.

### 4. Prerequisites
- **Node.js**: v18+ (for Frontend)
- **Python**: v3.10+ (for Backend AI Engine)
- **Database**: SQL Server 2019/2022 Developer Edition
- **MISA AMIS Account**: Valid Service Token or MISA CRM credentials.
