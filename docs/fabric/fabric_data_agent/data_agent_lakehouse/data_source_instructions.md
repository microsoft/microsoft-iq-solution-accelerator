# Data Source Instructions - Fabric Lakehouse

## Purpose

This document provides **query and usage guidance** for each data source in the lakehouse. It is a companion to `data_source_description.md`, which documents table schemas and field definitions.

While `data_source_description.md` answers *what is in the data*, this document answers *how to correctly query and use it* — including required filters, join patterns, aggregation rules, NULL handling, and cross-domain query patterns.

---

## General Rules (Apply to All Sources)

- **Always filter active records** unless the user explicitly asks for inactive or historical ones:
  - Customers: `WHERE IsActive = true`
  - Products: `WHERE ProductStatus = 'active'`
  - Product Categories: `WHERE IsActive = true`
  - Warehouses: `WHERE Status = 'Active'`
  - Finance Accounts: `WHERE AccountStatus = 'Active'`
- **Never expose raw GUID/ID fields** in responses. Reference human-readable names (e.g., `ProductName`, `CustomerRelationshipTypeName`, `WarehouseName`) unless the user explicitly asks for IDs.
- **Use schema-qualified table names** in all SQL: `customer.Customer`, `sales.Order`, `inventory.Inventory`, etc.
- **Select specific columns**, never `SELECT *`, to avoid pulling unnecessary data.

---

## Customer Domain (`customer` schema)

### Required Filters
- Use `IsActive = true` on `customer.Customer` unless historical customer data is needed.
- Use `PeriodEndDate IS NULL` on `customer.CustomerTradeName` to get the current active trade name only.

### Key Join Patterns

**Customer → Location** (for geographic analysis):
```sql
SELECT c.FirstName, c.LastName, l.City, l.StateId, l.Region
FROM customer.Customer c
JOIN customer.Location l ON c.CustomerId = l.CustomerId
WHERE c.IsActive = true AND l.IsActive = true
```

**Customer → Relationship Tier** (for segmentation):
```sql
SELECT c.FirstName, c.LastName, rt.CustomerRelationshipTypeName
FROM customer.Customer c
JOIN customer.CustomerRelationshipType rt
  ON c.CustomerRelationshipTypeId = rt.CustomerRelationshipTypeId
WHERE c.IsActive = true
```

**Customer → Account** (for financial linkage):
```sql
SELECT c.FirstName, c.LastName, ca.CustomerAccountName, ca.IsoCurrencyCode
FROM customer.Customer c
JOIN customer.CustomerAccount ca ON c.CustomerId = ca.CustomerId
WHERE c.IsActive = true
```

### Notes
- A customer can have **multiple locations** — always join to `customer.Location` for address data, not `customer.Customer` directly.
- The `Region` field on `customer.Location` (Northeast, West Coast, Midwest, South, etc.) is the preferred field for geographic segmentation, not `StateId`.
- `CustomerTypeId` (Individual, Business, Government) and `CustomerRelationshipTypeId` are separate concepts: type describes the customer's legal entity, relationship tier describes their service level.
- Individual customers use tiers: Standard, Premium, VIP. Business: SMB, Premier, Partner. Government: Federal, State, Local.

---

## Product Domain (`product` schema)

### Required Filters
- Use `ProductStatus = 'active'` on `product.Product` for current catalog queries.
- Use `SellEndDate IS NULL` as an additional check when looking for currently purchasable products.
- Use `IsActive = true` on `product.ProductCategory` for active categories.

### Key Join Patterns

**Product → Category**:
```sql
SELECT p.ProductName, p.ListPrice, p.StandardCost, cat.CategoryName
FROM product.Product p
JOIN product.ProductCategory cat ON p.ProductCategoryID = cat.CategoryID
WHERE p.ProductStatus = 'active' AND cat.IsActive = true
```

### Derived Calculations
- **Gross Margin** = `(ListPrice - StandardCost) / ListPrice * 100`  → expressed as a percentage
- **Margin Amount** = `ListPrice - StandardCost`

### Notes
- `CategoryName` is denormalized on `product.Product` — you can often avoid joining to `product.ProductCategory` when only the category name is needed.
- Three top-level product categories: **Camping**, **Kitchen**, **Ski**. Use these values for `WHERE CategoryName IN (...)` filters.
- `ProductStatus = 'discontinued'` records remain in the table for historical sales lookups — exclude them in catalog queries.

---

## Sales Domain (`sales` schema)

### Required Filters
- Use `OrderStatus = 'Completed'` for revenue and financial reporting to exclude cancelled or pending orders.
- For date-range queries, filter on `OrderDate` with explicit date bounds.

### Key Join Patterns

**Order → Line Items → Products** (revenue by product):
```sql
SELECT ol.ProductName, SUM(ol.LineTotal) AS TotalRevenue, SUM(ol.Quantity) AS UnitsSold
FROM sales.Order o
JOIN sales.OrderLine ol ON o.OrderId = ol.OrderId
WHERE o.OrderStatus = 'Completed'
  AND o.OrderDate BETWEEN '2025-01-01' AND '2025-12-31'
GROUP BY ol.ProductName
ORDER BY TotalRevenue DESC
```

**Order → Customer** (customer sales history):
```sql
SELECT c.FirstName, c.LastName, COUNT(o.OrderId) AS OrderCount, SUM(o.OrderTotal) AS TotalSpend
FROM sales.Order o
JOIN customer.Customer c ON o.CustomerId = c.CustomerId
WHERE o.OrderStatus = 'Completed'
GROUP BY c.FirstName, c.LastName
ORDER BY TotalSpend DESC
```

**Revenue by Category** (requires joining through OrderLine to Product):
```sql
SELECT p.CategoryName, SUM(ol.LineTotal) AS Revenue
FROM sales.OrderLine ol
JOIN product.Product p ON ol.ProductId = p.ProductID
JOIN sales.Order o ON ol.OrderId = o.OrderId
WHERE o.OrderStatus = 'Completed'
GROUP BY p.CategoryName
```

### Derived Calculations
- **Average Order Value** = `AVG(OrderTotal)` on `sales.Order WHERE OrderStatus = 'Completed'`
- **Gross Margin at Order Line** = `((ol.UnitPrice - p.StandardCost) / ol.UnitPrice) * 100`  → requires joining `product.Product`
- **Tax Rate**: Always 5% flat — `TaxAmount = SubTotal * 0.05`
- **Net Line Revenue** = `LineTotal - DiscountAmount`

### Notes
- `PaymentMethod` values: VISA, MC (MasterCard), Discover, PayPal.
- `OrderLine.ProductName` is denormalized — use it directly when only the name is needed; join to `product.Product` only when you need pricing, category, or cost information.
- `sales.OrderPayment` is a secondary payment record table. For most revenue reporting, use `sales.Order.OrderTotal` directly — do not double-count by summing both.

---

## Finance Domain (`finance` schema)

### Required Filters
- For outstanding receivables: `InvoiceStatus IN ('Pending', 'Overdue')` on `finance.invoice`.
- For active accounts: `AccountStatus = 'Active'` and `ClosedDate IS NULL` on `finance.account`.
- For successful payment totals: `PaymentStatus = 'Completed'` on `finance.payment`.

### Key Join Patterns

**Invoice Aging** (overdue invoices):
```sql
SELECT inv.InvoiceNumber, c.FirstName, c.LastName, inv.TotalAmount, inv.DueDate
FROM finance.invoice inv
JOIN customer.Customer c ON inv.CustomerId = c.CustomerId
WHERE inv.InvoiceStatus = 'Overdue'
ORDER BY inv.DueDate ASC
```

**Invoice → Payment reconciliation**:
```sql
SELECT inv.InvoiceNumber, inv.TotalAmount, p.PaymentAmount, p.PaymentStatus
FROM finance.invoice inv
LEFT JOIN finance.payment p ON inv.InvoiceId = p.InvoiceId
WHERE inv.InvoiceStatus != 'Cancelled'
```

**Account balance by customer type**:
```sql
SELECT c.CustomerTypeId, SUM(a.Balance) AS TotalBalance
FROM finance.account a
JOIN customer.Customer c ON a.CustomerId = c.CustomerId
WHERE a.AccountStatus = 'Active' AND a.AccountType = 'Receivable'
GROUP BY c.CustomerTypeId
```

### Notes
- One-to-one relationship between `sales.Order` and `finance.invoice` — each completed order has one invoice.
- `AccountType = 'Receivable'` represents money owed TO the company (most reporting focuses on this).
- Negative `Balance` on a Receivable account indicates credit/overpayment.
- `InvoiceStatus` transitions: Pending → Paid (or Overdue if past DueDate). Cancelled invoices should be excluded from all financial totals.

---

## Inventory Domain (`inventory` schema)

### Required Filters
- Active warehouses only: `WHERE Status = 'Active'` on `inventory.Warehouses`.
- For stock alerts: filter on `Status IN ('Low Stock', 'Out of Stock')` in `inventory.Inventory`.
- For open/in-transit purchase orders: `WHERE Status IN ('Pending', 'Shipped')` on `inventory.PurchaseOrders`.

### Key Join Patterns

**Current stock levels by product**:
```sql
SELECT i.ProductName, i.ProductCategory, w.WarehouseName, w.Type AS WarehouseType,
       i.CurrentStock, i.AvailableStock, i.ReorderPoint, i.SafetyStockLevel, i.Status
FROM inventory.Inventory i
JOIN inventory.Warehouses w ON i.WarehouseLocation = w.WarehouseName
WHERE w.Status = 'Active'
ORDER BY i.AvailableStock ASC
```

**Products below reorder point**:
```sql
SELECT i.ProductName, i.ProductCategory, i.AvailableStock, i.ReorderPoint, i.Status
FROM inventory.Inventory i
JOIN inventory.Warehouses w ON i.WarehouseLocation = w.WarehouseName
WHERE w.Status = 'Active'
  AND i.AvailableStock <= i.ReorderPoint
ORDER BY (i.AvailableStock - i.ReorderPoint) ASC
```

**Open purchase orders with expected delivery**:
```sql
SELECT po.PurchaseOrderNumber, po.SupplierName, po.ExpectedDeliveryDate,
       po.TotalOrderValue, po.Status, po.Priority
FROM inventory.PurchaseOrders po
WHERE po.Status IN ('Pending', 'Shipped')
ORDER BY po.ExpectedDeliveryDate ASC
```

**Inventory transaction history for a product**:
```sql
SELECT it.TransactionDate, it.TransactionType, it.Quantity,
       it.StockBefore, it.StockAfter, it.ReasonCode, it.ReferenceNumber
FROM inventory.InventoryTransactions it
WHERE it.ProductName = '<ProductName>'
ORDER BY it.TransactionDate DESC
```

### Derived Calculations
- **Available Stock** = `CurrentStock - ReservedStock` (already stored in `AvailableStock`, but verify if computing manually)
- **Inventory Value** = `AvailableStock * AverageCost`
- **Stock Coverage Days** = `AvailableStock / (PredictedDemand / ForecastDays)` — requires joining to `inventory.DemandForecast`
- **Warehouse Utilization** = `SUM(CurrentStock) / MAX(MaxCapacity)` — join `inventory.Inventory` to `inventory.Warehouses`

### Notes
- `ActualDeliveryDate IS NULL` on `inventory.PurchaseOrders` means the order has NOT yet been delivered — use `ExpectedDeliveryDate` for ETA.
- `inventory.DemandForecast` data is pre-generated synthetic forecasts, not live ML predictions. Treat `ConfidenceLevel` as indicative only.
- `TrendDirection` values on `DemandForecast`: Growing, Stable, Declining — flag declining trends when users ask about risk.
- `inventory.InventoryTransactions` is the audit trail — use it for historical stock movement analysis, not current stock levels.

---

## Supply Chain Domain (`supplychain` schema)

### Required Filters
- Active suppliers only: `WHERE Status = 'Active'` on `supplychain.Suppliers`.
- Active disruptions: `WHERE Status IN ('Active', 'Monitoring')` on `supplychain.SupplyChainEvents`.
- `EndDate IS NULL` on `supplychain.SupplyChainEvents` indicates an ongoing disruption with no end date.

### Key Join Patterns

**Products with multiple suppliers** (redundancy check):
```sql
SELECT ps.ProductName, ps.ProductCategory, COUNT(ps.SupplierName) AS SupplierCount,
       STRING_AGG(ps.SupplierName, ', ') AS Suppliers
FROM supplychain.ProductSuppliers ps
JOIN supplychain.Suppliers s ON ps.SupplierName = s.SupplierName
WHERE s.Status = 'Active' AND ps.Status = 'Active'
GROUP BY ps.ProductName, ps.ProductCategory
ORDER BY SupplierCount DESC
```

**Active supply chain disruptions**:
```sql
SELECT e.EventName, e.DisruptionType, e.Severity, e.AlertLevel,
       e.GeographicArea, e.StartDate, e.EndDate,
       e.DeliveryDelay, e.CostIncrease, e.EstimatedRevenueImpact, e.AlternativeAction
FROM supplychain.SupplyChainEvents e
WHERE e.Status IN ('Active', 'Monitoring')
ORDER BY 
  CASE e.Severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
  e.StartDate DESC
```

**Supplier lead time vs. current inventory** (risk assessment):
```sql
SELECT ps.ProductName, ps.ProductCategory, ps.SupplierName,
       ps.LeadTimeDays, i.AvailableStock, i.ReorderPoint,
       (i.AvailableStock - i.ReorderPoint) AS StockBuffer
FROM supplychain.ProductSuppliers ps
JOIN inventory.Inventory i ON ps.ProductName = i.ProductName
JOIN supplychain.Suppliers s ON ps.SupplierName = s.SupplierName
WHERE s.Status = 'Active' AND ps.Status = 'Active'
ORDER BY ps.LeadTimeDays DESC, StockBuffer ASC
```

### Notes
- `SupplierType`: Primary = main supplier; Secondary = backup supplier. Always note which type when listing suppliers.
- `ReliabilityScore` (0–100) on `supplychain.Suppliers` indicates supplier dependability — scores below 70 suggest risk.
- Supplier network summary: 3 Primary suppliers (Contoso Ltd, Proseware Inc, Alpine Ski House), 2 Secondary (Worldwide Importers, Fabrikam).
- `AlertLevel` on events: Green (low impact) → Yellow → Orange → Red (critical). Prioritize Red/Orange in risk summaries.

---

## Cross-Domain Query Patterns

### Customer Lifetime Value
Combines `customer`, `sales`, and `finance` domains:
```sql
SELECT c.FirstName, c.LastName, c.CustomerTypeId, rt.CustomerRelationshipTypeName,
       COUNT(DISTINCT o.OrderId) AS TotalOrders,
       SUM(o.OrderTotal) AS LifetimeRevenue,
       AVG(o.OrderTotal) AS AvgOrderValue
FROM customer.Customer c
JOIN customer.CustomerRelationshipType rt ON c.CustomerRelationshipTypeId = rt.CustomerRelationshipTypeId
JOIN sales.Order o ON c.CustomerId = o.CustomerId
WHERE c.IsActive = true AND o.OrderStatus = 'Completed'
GROUP BY c.FirstName, c.LastName, c.CustomerTypeId, rt.CustomerRelationshipTypeName
ORDER BY LifetimeRevenue DESC
```

### Revenue vs. Inventory Risk
Combines `sales`, `inventory`, and `supplychain` domains:
```sql
SELECT ol.ProductName, p.CategoryName,
       SUM(ol.LineTotal) AS TotalRevenue,
       i.AvailableStock, i.ReorderPoint, i.Status AS StockStatus
FROM sales.OrderLine ol
JOIN sales.Order o ON ol.OrderId = o.OrderId
JOIN product.Product p ON ol.ProductId = p.ProductID
JOIN inventory.Inventory i ON ol.ProductName = i.ProductName
WHERE o.OrderStatus = 'Completed'
  AND o.OrderDate >= DATEADD(month, -3, CURRENT_DATE)
GROUP BY ol.ProductName, p.CategoryName, i.AvailableStock, i.ReorderPoint, i.Status
ORDER BY TotalRevenue DESC
```

### Invoice Collection Efficiency
Combines `finance` and `customer` domains:
```sql
SELECT c.CustomerTypeId, rt.CustomerRelationshipTypeName,
       COUNT(inv.InvoiceId) AS TotalInvoices,
       SUM(CASE WHEN inv.InvoiceStatus = 'Paid' THEN inv.TotalAmount ELSE 0 END) AS PaidAmount,
       SUM(CASE WHEN inv.InvoiceStatus = 'Overdue' THEN inv.TotalAmount ELSE 0 END) AS OverdueAmount
FROM finance.invoice inv
JOIN customer.Customer c ON inv.CustomerId = c.CustomerId
JOIN customer.CustomerRelationshipType rt ON c.CustomerRelationshipTypeId = rt.CustomerRelationshipTypeId
WHERE inv.InvoiceStatus != 'Cancelled'
GROUP BY c.CustomerTypeId, rt.CustomerRelationshipTypeName
```

---

## Common Pitfalls

| Pitfall | Correct Approach |
|---------|-----------------|
| Summing `sales.Order.OrderTotal` AND `finance.invoice.TotalAmount` for the same period | Use only one source — they represent the same amounts. Prefer `sales.Order` for sales revenue, `finance.invoice` for billing/AR reporting. |
| Joining `inventory.InventoryTransactions` for current stock levels | Use `inventory.Inventory` for current/available stock. `InventoryTransactions` is audit history only. |
| Counting all orders including Pending and Cancelled | Always apply `WHERE OrderStatus = 'Completed'` unless tracking order pipeline. |
| Treating `finance.payment.PaymentAmount` as distinct from `sales.Order.OrderTotal` | They represent the same transaction. Avoid joining both for revenue totals. |
| Using `customer.Customer.Region` for geographic segmentation | `Region` is on `customer.Location`, not `customer.Customer`. Always join to `customer.Location`. |
| Assuming one customer → one location | Customers can have multiple locations. Use `l.IsActive = true` and consider if you need a specific location type. |
| Assuming all demand forecasts are reliable | `inventory.DemandForecast` is synthetic pre-generated data. Use `ConfidenceLevel` as a qualifier — flag low-confidence forecasts. |
