-- Fabric notebook source

-- METADATA ********************

-- META {
-- META   "kernel_info": {
-- META     "name": "synapse_pyspark"
-- META   }
-- META }

-- CELL ********************

-- Use this in Fabric Warehouse UI
-- T-SQL Query: Sales Channel Analytics - Comprehensive metrics by SalesChannelId
-- Source: Combined data from Order_Samples_Camping.csv, Order_Samples_Kitchen.csv, Order_Samples_Ski.csv
-- Table: [fabriciq_team_lake].[sales].[order]
-- 
-- Returns: Order counts, percentages, unique customers, revenue totals, average order values, and date ranges

SELECT 
    SalesChannelId,
    COUNT(*) AS OrderCount,
    CAST(ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS DECIMAL(5,2)) AS Percentage,
    COUNT(DISTINCT CustomerId) AS UniqueCustomers,
    FORMAT(SUM(OrderTotal), 'N2') AS TotalRevenue,
    FORMAT(AVG(OrderTotal), 'N2') AS AvgOrderValue,
    MIN(OrderDate) AS FirstOrderDate,
    MAX(OrderDate) AS LastOrderDate
FROM [fabriciq_team_lake].[sales].[order]
GROUP BY SalesChannelId
ORDER BY SUM(OrderTotal) DESC;

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }
