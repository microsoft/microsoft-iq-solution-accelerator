# Query Examples — Fabric IQ Data Agent

This document provides example natural language questions and their corresponding SQL queries for the Fabric lakehouse. These examples demonstrate how to query across the six business domains and serve as reference patterns for building and validating agent responses.

---

## Example 1: Customer Segmentation by Relationship Tier and Region

**Question**: I need to understand our customer base better. Can you show me a breakdown of customers by relationship type and geographic region, including how many are active vs. inactive? I want to see which segments and regions we should focus on for our upcoming marketing campaign.

**Example Query**:

```sql
-- 1. Customer Segmentation: count by relationship tier, customer type, and region
SELECT
    rt.CustomerRelationshipTypeName     AS RelationshipTier,
    c.CustomerTypeID                    AS CustomerType,
    l.Region,
    COUNT(*)                            AS TotalCustomers,
    SUM(CASE WHEN c.IsActive = 1 THEN 1 ELSE 0 END) AS Active,
    SUM(CASE WHEN c.IsActive = 0 THEN 1 ELSE 0 END) AS Inactive
FROM customer.customer c
JOIN customer.customerrelationshiptype rt
    ON c.CustomerRelationshipTypeID = rt.CustomerRelationshipTypeID
JOIN customer.location l
    ON c.CustomerID = l.CustomerID
WHERE l.IsActive = 1
GROUP BY rt.CustomerRelationshipTypeName, c.CustomerTypeID, l.Region
ORDER BY TotalCustomers DESC, l.Region;
```

---

## Example 2: Sales Revenue and Margin by Product Category

**Question**: How are our three product categories — Camping, Kitchen, and Ski — performing year-to-date in terms of orders, units sold, gross revenue, and net revenue after discounts?

**Example Query**:

```sql
-- 2. Sales revenue and units by product category, year-to-date
SELECT
    p.CategoryName                                          AS Category,
    COUNT(DISTINCT o.OrderID)                               AS Orders,
    SUM(ol.Quantity)                                        AS UnitsSold,
    CAST(SUM(ol.LineTotal) AS DECIMAL(18,2))                AS GrossRevenue,
    CAST(SUM(ol.DiscountAmount) AS DECIMAL(18,2))           AS Discounts,
    CAST(SUM(ol.LineTotal - ol.DiscountAmount) AS DECIMAL(18,2)) AS NetRevenue
FROM sales.[order] o
JOIN sales.orderline ol ON o.OrderID = ol.OrderID
JOIN product.product p  ON ol.ProductID = p.ProductID
WHERE o.OrderStatus = 'Completed'
  AND o.OrderDate >= DATEADD(year, DATEDIFF(year, 0, GETDATE()), 0)
GROUP BY p.CategoryName
ORDER BY NetRevenue DESC;
```

---

## Example 3: Inventory Stock Health and Reorder Risk

**Question**: Which products across our active warehouses are at or below their reorder point? Show me the available stock, reorder point, safety stock level, and current stock status so I can identify what needs attention.

**Example Query**:

```sql
-- 3. Products at or below reorder point across active warehouses
SELECT
    i.ProductName,
    i.ProductCategory               AS Category,
    w.WarehouseName                 AS Warehouse,
    i.AvailableStock,
    i.ReorderPoint,
    i.SafetyStockLevel              AS SafetyStock,
    i.AvailableStock - i.ReorderPoint AS StockBuffer,
    i.Status                        AS StockStatus
FROM inventory.inventory i
JOIN inventory.warehouses w ON i.WarehouseLocation = w.WarehouseName
WHERE w.Status = 'Active'
  AND i.AvailableStock <= i.ReorderPoint
ORDER BY i.AvailableStock ASC;
```
---

## Example 4: Supply Chain Risk Assessment with Inventory Impact

**Question**: Are there any active or monitored supply chain disruptions we should be worried about? For each disruption, I want to know the severity, which suppliers and product categories are affected, expected delivery delays, estimated revenue impact, and the recommended action.

**Example Query**:

```sql
-- 4. Active and monitored supply chain disruptions with supplier details
SELECT
    e.EventName,
    e.DisruptionType,
    e.Severity,
    e.AlertLevel,
    e.Status,
    e.GeographicArea              AS AreaAffected,
    e.StartDate,
    e.EndDate,
    e.DeliveryDelay               AS DelayDays,
    e.EstimatedRevenueImpact      AS EstRevenueImpact,
    e.AlternativeAction           AS RecommendedAction,
    e.ProductCategory,
    s.SupplierName,
    s.SupplierType,
    s.ReliabilityScore
FROM supplychain.supplychainevents e
LEFT JOIN supplychain.suppliers s ON e.SupplierID = s.SupplierID
WHERE e.Status IN ('Active', 'Monitoring')
ORDER BY
    CASE e.Severity
        WHEN 'Critical' THEN 1
        WHEN 'High'     THEN 2
        WHEN 'Medium'   THEN 3
        ELSE 4
    END,
    e.StartDate DESC;
```

---

## Example 5: Supplier Reliability and Lead Time Analysis

**Question**: I want to evaluate how reliable our suppliers are and whether their lead times are putting us at risk. Can you show me each supplier's reliability score, their average lead time per product category, how many products they supply, and flag any suppliers that are currently disrupted or have a reliability score below 70?

**Example Query**:

```sql
-- 5. Supplier reliability scores and average lead time per category
SELECT
    s.SupplierName,
    s.SupplierType,
    s.ProductCategory,
    s.Status                        AS SupplierStatus,
    s.ReliabilityScore,
    CASE
        WHEN s.ReliabilityScore >= 85 THEN 'Good'
        WHEN s.ReliabilityScore >= 70 THEN 'Acceptable'
        ELSE 'AT RISK'
    END                             AS ReliabilityRating,
    AVG(ps.LeadTimeDays)            AS AvgLeadTimeDays,
    COUNT(DISTINCT ps.ProductName)  AS ProductsSupplied
FROM supplychain.suppliers s
JOIN supplychain.productsuppliers ps ON s.SupplierName = ps.SupplierName
WHERE s.Status = 'Active'
  AND ps.Status = 'Active'
GROUP BY s.SupplierName, s.SupplierType, s.ProductCategory, s.Status, s.ReliabilityScore
ORDER BY s.ReliabilityScore ASC, s.ProductCategory;
```