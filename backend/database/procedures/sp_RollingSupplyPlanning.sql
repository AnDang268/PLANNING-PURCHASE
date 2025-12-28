CREATE OR ALTER PROCEDURE sp_RollingSupplyPlanning
    @HorizonMonths INT = 12,
    @ProfileID NVARCHAR(50) = 'STD',
    @GroupID NVARCHAR(50) = NULL,
    @WarehouseID NVARCHAR(50) = 'ALL',
    @RunDate DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;

    -- 1. Configuration & Time Setup
    DECLARE @StartDate DATE;
    IF @RunDate IS NOT NULL
        SET @StartDate = DATEADD(dd, -(DATEPART(dw, @RunDate)-1), CAST(@RunDate AS DATE));
    ELSE
        SET @StartDate = DATEADD(dd, -(DATEPART(dw, GETDATE())-1), CAST(GETDATE() AS DATE));

    DECLARE @EndDate DATE = DATEADD(MONTH, @HorizonMonths, @StartDate);

    -- 2. Filter Scope (Products) & Dictionary
    CREATE TABLE #ProductParams (
        sku_id NVARCHAR(50) PRIMARY KEY,
        avg_sales FLOAT,
        safety_days INT,
        moq FLOAT
    );
    
    -- Default Policy (fallback)
    DECLARE @DefaultSafetyDays INT = 15;
    SELECT TOP 1 @DefaultSafetyDays = safety_stock_days FROM Planning_Policies WHERE is_default = 1;

    INSERT INTO #ProductParams (sku_id, avg_sales, safety_days, moq)
    SELECT 
        p.sku_id, 
        ISNULL(p.avg_weekly_sales, 0),
        ISNULL(pol.safety_stock_days, @DefaultSafetyDays),
        ISNULL(NULLIF(p.moq, 0), 1)
    FROM Dim_Products p
    LEFT JOIN Planning_Policies pol ON p.policy_id = pol.policy_id
    WHERE (@GroupID IS NULL OR p.group_id = @GroupID OR p.category = @GroupID)
      AND (@GroupID <> 'ALL' OR @GroupID IS NULL);

    -- 3. Cleanup Existing Data
    DELETE T
    FROM Fact_Rolling_Inventory T
    INNER JOIN #ProductParams S ON T.sku_id = S.sku_id
    WHERE T.bucket_date >= @StartDate 
      AND T.bucket_date <= @EndDate
      AND ((@WarehouseID IS NULL) OR (T.warehouse_id = @WarehouseID))
      AND T.profile_id = @ProfileID;

    -- 4. Prepare Temporary Tables
    CREATE TABLE #Buckets (BucketDate DATE PRIMARY KEY);
    DECLARE @CurrentDate DATE = @StartDate;
    WHILE @CurrentDate <= @EndDate
    BEGIN
        INSERT INTO #Buckets (BucketDate) VALUES (@CurrentDate);
        SET @CurrentDate = DATEADD(WEEK, 1, @CurrentDate);
    END

    -- #Forecasts (Filtered by SKU & Split by Week)
    -- Logic: 
    -- 1. Get Monthly Forecast
    -- 2. Join with Profile
    -- 3. Split into 4 Weeks starting from 1st of Month
    
    SELECT 
        f.sku_id, 
        CAST(DATEADD(WEEK, W.WeekIdx - 1, f.forecast_date) AS DATE) as FDate, 
        SUM(f.quantity_predicted * 
            CASE W.WeekIdx
                WHEN 1 THEN COALESCE(prof.week1, 0.25)
                WHEN 2 THEN COALESCE(prof.week2, 0.25)
                WHEN 3 THEN COALESCE(prof.week3, 0.25)
                WHEN 4 THEN COALESCE(prof.week4, 0.25)
                ELSE 0
            END
        ) as Qty
    INTO #Forecasts
    FROM Fact_Forecasts f
    INNER JOIN #ProductParams s ON f.sku_id = s.sku_id
    LEFT JOIN Dim_Products p ON f.sku_id = p.sku_id
    LEFT JOIN Planning_Distribution_Profiles prof ON prof.profile_id = COALESCE(p.distribution_profile_id, @ProfileID) -- Priority: Product > Global Run Profile
    CROSS JOIN (VALUES (1), (2), (3), (4)) AS W(WeekIdx) -- Expand 1 Month -> 4 Weeks
    WHERE f.forecast_date BETWEEN DATEADD(MONTH, -1, @StartDate) AND @EndDate -- optimization
      AND DAY(f.forecast_date) = 1 -- Assuming Forecasts are stored as 1st of Month
    GROUP BY f.sku_id, CAST(DATEADD(WEEK, W.WeekIdx - 1, f.forecast_date) AS DATE);
    
    CREATE CLUSTERED INDEX IX_Forecasts ON #Forecasts(sku_id, FDate);

    -- #Incoming (Filtered by SKU)
    SELECT p.sku_id, CAST(p.order_date AS DATE) as PDate, SUM(p.quantity) as Qty
    INTO #Incoming
    FROM Fact_Purchases p
    INNER JOIN #ProductParams s ON p.sku_id = s.sku_id
    WHERE p.order_date BETWEEN @StartDate AND @EndDate
    GROUP BY p.sku_id, CAST(p.order_date AS DATE);
    
    CREATE CLUSTERED INDEX IX_Incoming ON #Incoming(sku_id, PDate);

    -- #InitialStock (Filtered by Warehouse & SKU)
    SELECT os.sku_id, SUM(os.quantity) as Qty
    INTO #InitialStock
    FROM Fact_Opening_Stock os
    INNER JOIN #ProductParams s ON os.sku_id = s.sku_id
    WHERE os.stock_date = (SELECT MAX(stock_date) FROM Fact_Opening_Stock WHERE stock_date <= @StartDate)
      AND (@WarehouseID IS NULL OR os.warehouse_id = @WarehouseID OR @WarehouseID = 'ALL')
    GROUP BY os.sku_id;

    -- 5. Rolling Calculation Loop
    CREATE TABLE #RunningState (
        sku_id NVARCHAR(50) PRIMARY KEY,
        CurrentStock FLOAT
    );

    -- Init State
    INSERT INTO #RunningState (sku_id, CurrentStock)
    SELECT s.sku_id, ISNULL(init.Qty, 0)
    FROM #ProductParams s
    LEFT JOIN #InitialStock init ON s.sku_id = init.sku_id;

    DECLARE @WeekCursor DATE;
    DECLARE BucketCursor CURSOR LOCAL FAST_FORWARD FOR
    SELECT BucketDate FROM #Buckets ORDER BY BucketDate;

    OPEN BucketCursor;
    FETCH NEXT FROM BucketCursor INTO @WeekCursor;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Insert Step: Snapshot Current State
        -- MinStock = (AvgWeekly / 7) * SafetyDays
        INSERT INTO Fact_Rolling_Inventory (sku_id, warehouse_id, bucket_date, profile_id, opening_stock, forecast_demand, incoming_supply, planned_supply, closing_stock, net_requirement, min_stock_policy)
        SELECT 
            st.sku_id,
            @WarehouseID,
            @WeekCursor,
            @ProfileID,
            st.CurrentStock,
            ISNULL(fc.Qty, 0),
            ISNULL(inc.Qty, 0),
            0, 
            0, 
            0, 
            (p.avg_sales / 7.0) * p.safety_days -- Dynamic Min Stock
        FROM #RunningState st
        INNER JOIN #ProductParams p ON st.sku_id = p.sku_id
        LEFT JOIN (
            SELECT sku_id, SUM(Qty) as Qty 
            FROM #Forecasts 
            WHERE FDate >= @WeekCursor AND FDate < DATEADD(DAY, 7, @WeekCursor)
            GROUP BY sku_id
        ) fc ON st.sku_id = fc.sku_id
        LEFT JOIN (
            SELECT sku_id, SUM(Qty) as Qty 
            FROM #Incoming 
            WHERE PDate >= @WeekCursor AND PDate < DATEADD(DAY, 7, @WeekCursor)
            GROUP BY sku_id
        ) inc ON st.sku_id = inc.sku_id;

        -- Update Calculation Step: Use Dynamic MinStock
        UPDATE T
        SET 
            net_requirement = CASE 
                WHEN (ISNULL(opening_stock, 0) + ISNULL(incoming_supply, 0) - ISNULL(forecast_demand, 0)) < T.min_stock_policy 
                THEN (T.min_stock_policy - (ISNULL(opening_stock, 0) + ISNULL(incoming_supply, 0) - ISNULL(forecast_demand, 0)))
                ELSE 0 
            END
        FROM Fact_Rolling_Inventory T
        WHERE T.bucket_date = @WeekCursor AND T.warehouse_id = @WarehouseID AND T.profile_id = @ProfileID;

        -- 2. Planned Supply = Roundup(NetReq / MOQ) * MOQ
        UPDATE T
        SET planned_supply = CASE 
                WHEN net_requirement > 0 
                THEN CEILING(net_requirement / p.moq) * p.moq
                ELSE 0 
            END
        FROM Fact_Rolling_Inventory T
        INNER JOIN #ProductParams p ON T.sku_id = p.sku_id
        WHERE T.bucket_date = @WeekCursor AND T.warehouse_id = @WarehouseID AND T.profile_id = @ProfileID;

        -- 3. Closing Stock
        UPDATE T
        SET closing_stock = ISNULL(opening_stock, 0) + ISNULL(incoming_supply, 0) + ISNULL(planned_supply, 0) - ISNULL(forecast_demand, 0)
        FROM Fact_Rolling_Inventory T
        WHERE T.bucket_date = @WeekCursor AND T.warehouse_id = @WarehouseID AND T.profile_id = @ProfileID;

        -- 4. Pass Closing to Next Opening
        UPDATE S
        SET S.CurrentStock = T.closing_stock
        FROM #RunningState S
        INNER JOIN Fact_Rolling_Inventory T ON S.sku_id = T.sku_id
        WHERE T.bucket_date = @WeekCursor AND T.warehouse_id = @WarehouseID AND T.profile_id = @ProfileID;

        FETCH NEXT FROM BucketCursor INTO @WeekCursor;
    END

    CLOSE BucketCursor;
    DEALLOCATE BucketCursor;

    -- Cleanup
    DROP TABLE #Buckets;
    DROP TABLE #ProductParams; -- Renamed from #TargetSKUs
    DROP TABLE #Forecasts;
    DROP TABLE #Incoming;
    DROP TABLE #InitialStock;
    DROP TABLE #RunningState;

END
