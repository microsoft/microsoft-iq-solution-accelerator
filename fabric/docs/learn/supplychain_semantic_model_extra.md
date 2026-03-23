# Supply Chain Semantic Model — Concepts & Step-by-Step Guide

> Applies to the Fabric IQ semantic model built on:  
> `inventory` schema (6 tables) · `product` schema (2 tables) · `supplychain` schema (3 tables)

---

## Part 1: Core Concepts

### What is a Semantic Model?

Think of it as a **business-friendly lens over your raw tables**. Instead of writing SQL joins every time, users ask questions in plain English ("What is my total inventory value?") and Power BI or Fabric figures out the math using the rules you define once in the model.

Your semantic model sits on top of these 11 tables:

| Schema | Tables |
|---|---|
| `inventory` | Inventory, InventoryTransactions, PurchaseOrders, PurchaseOrderItems, Warehouses, DemandForecast |
| `product` | Product, ProductCategory |
| `supplychain` | Suppliers, ProductSuppliers, SupplyChainEvents |

---

### Concept 1: Measures

**What**: A calculation that runs against your data and gives you a single result (number, text, percentage).

**Why**: Instead of raw columns like `CurrentStock` and `AverageCost`, a measure calculates **Total Inventory Value** = `CurrentStock × AverageCost` automatically for whatever filter the user has applied (e.g., just Camping products, just the Main warehouse).

**Key rule**: Measures are dynamic — they recalculate based on context (what product, what warehouse, what time period the user is looking at).

**Your first 5 measures to build:**

| Measure Name | Business Question | Formula Logic |
|---|---|---|
| `Total Inventory Value` | How much is my stock worth? | `SUM(CurrentStock × AverageCost)` |
| `Available Stock Units` | How many units can I ship? | `SUM(AvailableStock)` |
| `Stock Coverage Days` | How many days before I run out? | `AvailableStock ÷ (30-day sales ÷ 30)` |
| `Total PO Value` | How much is on order? | `SUM(TotalOrderValue)` |
| `Forecast Accuracy %` | How reliable are my forecasts? | `1 - ABS(Predicted - Actual) / Actual` |

---

### Concept 2: Perspectives

**What**: A filtered view of the model that shows only the tables and measures relevant to a specific audience.

**Why**: Your model has 11 tables. A warehouse manager does not need to see supplier reliability scores. A procurement officer does not need DemandForecast internals. Perspectives let different users see a simplified, focused version.

**Your perspectives to create:**

| Perspective | Who Uses It | Tables Included |
|---|---|---|
| **Warehouse Operations** | Warehouse managers | Inventory, Warehouses, InventoryTransactions |
| **Procurement** | Buyers, purchasing team | PurchaseOrders, PurchaseOrderItems, Suppliers, ProductSuppliers |
| **Supply Chain Risk** | Risk manager, leadership | SupplyChainEvents, Suppliers, PurchaseOrders |
| **Demand Planning** | Planners | DemandForecast, Inventory, Product |
| **Product Catalog** | Category managers | Product, ProductCategory, ProductSuppliers |

---

### Concept 3: Calculation Groups

**What**: A way to reuse the same mathematical transformation across many measures by defining it once as a "calculation item."

**Why**: Suppose you have 10 measures (Total Inventory Value, PO Value, Forecast Demand, etc.) and you want to show them all as:
- Actual value
- Month-to-date (MTD)
- Year-to-date (YTD)
- vs Prior Period

Without calculation groups, you'd write 10 × 4 = **40 measures**. With a calculation group, you write **10 measures + 4 calculation items = 14 total**. The group applies the time logic to any measure automatically.

**Your calculation groups to create:**

| Calculation Group | Calculation Items | Applies To |
|---|---|---|
| **Time Intelligence** | Actual, MTD, QTD, YTD, Prior Period, % Change vs Prior | All date-based measures |
| **Stock Status View** | Available Only, Low Stock Only, Out of Stock Only, % vs Safety Stock | Stock quantity measures |
| **PO Fulfillment View** | Ordered, Received, Pending, Fulfillment % | PO quantity/value measures |

---

## Part 2: Step-by-Step Build Guide

### Step 1 — Set Up Your Table Relationships

Before adding measures, the tables must be linked correctly. In the Power BI / Fabric semantic model diagram view, create these joins:

```
Product.ProductID          ──→  Inventory.ProductID
Product.ProductID          ──→  InventoryTransactions.ProductID
Product.ProductID          ──→  PurchaseOrderItems.ProductID
Product.ProductID          ──→  DemandForecast.ProductID
Product.ProductID          ──→  ProductSuppliers.ProductID
Product.ProductCategoryID  ──→  ProductCategory.CategoryID

Warehouses.WarehouseID     ──→  Inventory.WarehouseLocation
Warehouses.WarehouseID     ──→  InventoryTransactions.WarehouseLocation
Warehouses.WarehouseID     ──→  PurchaseOrders.DeliveryLocation

PurchaseOrders.PurchaseOrderID  ──→  PurchaseOrderItems.PurchaseOrderID
PurchaseOrders.SupplierID       ──→  Suppliers.SupplierID

Suppliers.SupplierID  ──→  ProductSuppliers.SupplierID
Suppliers.SupplierID  ──→  SupplyChainEvents.SupplierID
```

> **Tip**: Use **single-direction** relationships for most of these. Only use bidirectional if you need to filter both ways — generally avoid this to prevent ambiguous results.

---

### Step 2 — Build Your Core Measures

Open the model in Fabric or Power BI Desktop. Create a dedicated **"Measures"** table (a blank table used purely for organizing measures — a common best practice). Then add these measures using DAX:

#### Inventory Measures

```dax
-- How much is our stock worth right now?
Total Inventory Value =
SUMX(
    inventory_Inventory,
    inventory_Inventory[CurrentStock] * inventory_Inventory[AverageCost]
)
```

```dax
-- Total units available to ship
Available Stock Units =
SUM(inventory_Inventory[AvailableStock])
```

```dax
-- Units that are reserved/allocated but not yet shipped
Reserved Stock Units =
SUM(inventory_Inventory[ReservedStock])
```

```dax
-- How many products have stock below reorder point?
Products Below Reorder Point =
CALCULATE(
    COUNTROWS(inventory_Inventory),
    inventory_Inventory[CurrentStock] <= inventory_Inventory[ReorderPoint]
)
```

```dax
-- Total units received via inventory transactions
Units Received =
CALCULATE(
    SUM(inventory_InventoryTransactions[Quantity]),
    inventory_InventoryTransactions[TransactionType] = "Receipt"
)
```

```dax
-- Total units consumed/sold
Units Consumed =
CALCULATE(
    SUM(inventory_InventoryTransactions[Quantity]),
    inventory_InventoryTransactions[TransactionType] = "Sale"
)
```

#### Purchase Order Measures

```dax
-- Total value of all purchase orders
Total PO Value =
SUM(inventory_PurchaseOrders[TotalOrderValue])
```

```dax
-- Value of open (pending/shipped) POs only
Open PO Value =
CALCULATE(
    SUM(inventory_PurchaseOrders[TotalOrderValue]),
    inventory_PurchaseOrders[Status] IN { "Pending", "Shipped" }
)
```

```dax
-- PO fulfillment rate: how much of what was ordered was actually received?
PO Fulfillment Rate % =
DIVIDE(
    SUM(inventory_PurchaseOrderItems[QuantityReceived]),
    SUM(inventory_PurchaseOrderItems[QuantityOrdered]),
    0
) * 100
```

```dax
-- Average lead time in days for delivered purchase orders
Avg Actual Lead Time Days =
AVERAGEX(
    FILTER(
        inventory_PurchaseOrders,
        NOT ISBLANK(inventory_PurchaseOrders[ActualDeliveryDate])
    ),
    DATEDIFF(
        inventory_PurchaseOrders[OrderDate],
        inventory_PurchaseOrders[ActualDeliveryDate],
        DAY
    )
)
```

#### Supply Chain Risk Measures

```dax
-- How many disruptions are currently active or being monitored?
Active Disruptions =
CALCULATE(
    COUNTROWS(supplychain_SupplyChainEvents),
    supplychain_SupplyChainEvents[Status] IN { "Active", "Monitoring" }
)
```

```dax
-- Total estimated revenue impact from active disruption events
Active Disruption Revenue Impact =
CALCULATE(
    SUM(supplychain_SupplyChainEvents[EstimatedRevenueImpact]),
    supplychain_SupplyChainEvents[Status] IN { "Active", "Monitoring" }
)
```

```dax
-- Average supplier reliability score across all active suppliers
Avg Supplier Reliability =
CALCULATE(
    AVERAGE(supplychain_Suppliers[ReliabilityScore]),
    supplychain_Suppliers[Status] = "Active"
)
```

#### Demand Forecast Measures

```dax
-- Total predicted demand across all forecasted periods
Total Predicted Demand =
SUM(inventory_DemandForecast[PredictedDemand])
```

```dax
-- Average forecast confidence level (0-100%)
Avg Forecast Confidence % =
AVERAGE(inventory_DemandForecast[ConfidenceLevel])
```

---

### Step 3 — Create the Time Intelligence Calculation Group

This is the most powerful step. It lets every date-based measure automatically work as MTD, YTD, etc. without duplicating logic.

#### First: Create a Date Table

You need a dedicated Date table in your model. Create one using this DAX:

```dax
Date Table =
CALENDAR(DATE(2025, 1, 1), DATE(2026, 12, 31))
```

Add these calculated columns to the Date table:

```dax
Year        = YEAR([Date])
Month       = MONTH([Date])
MonthName   = FORMAT([Date], "MMMM")
Quarter     = "Q" & QUARTER([Date])
YearMonth   = FORMAT([Date], "YYYY-MM")
WeekNumber  = WEEKNUM([Date])
```

Then:
1. Mark it as a **Date Table** in the model settings (right-click the table → Mark as Date Table → select the `Date` column)
2. Link it to your date columns:
   - `InventoryTransactions[TransactionDate]`
   - `PurchaseOrders[OrderDate]`
   - `DemandForecast[ForecastDate]`

#### Then: Create the Calculation Group

Use **Tabular Editor** to create this (see Tools section below). Name the group `Time Intelligence`:

| Calculation Item | DAX Formula |
|---|---|
| `Actual` | `SELECTEDMEASURE()` |
| `MTD` | `CALCULATE(SELECTEDMEASURE(), DATESMTD('Date Table'[Date]))` |
| `QTD` | `CALCULATE(SELECTEDMEASURE(), DATESQTD('Date Table'[Date]))` |
| `YTD` | `CALCULATE(SELECTEDMEASURE(), DATESYTD('Date Table'[Date]))` |
| `Prior Period` | `CALCULATE(SELECTEDMEASURE(), PREVIOUSMONTH('Date Table'[Date]))` |
| `% vs Prior Period` | `DIVIDE(SELECTEDMEASURE() - CALCULATE(SELECTEDMEASURE(), PREVIOUSMONTH('Date Table'[Date])), CALCULATE(SELECTEDMEASURE(), PREVIOUSMONTH('Date Table'[Date])), BLANK())` |

---

### Step 4 — Create the Stock Status Calculation Group

Name the group `Stock Status View`:

| Calculation Item | DAX Formula |
|---|---|
| `Available Only` | `CALCULATE(SELECTEDMEASURE(), inventory_Inventory[Status] = "Active")` |
| `Low Stock Only` | `CALCULATE(SELECTEDMEASURE(), inventory_Inventory[Status] = "Low Stock")` |
| `Out of Stock Only` | `CALCULATE(SELECTEDMEASURE(), inventory_Inventory[Status] = "Out of Stock")` |
| `% vs Safety Stock` | `DIVIDE(SELECTEDMEASURE(), SUM(inventory_Inventory[SafetyStockLevel]), BLANK())` |
| `% vs Reorder Point` | `DIVIDE(SELECTEDMEASURE(), SUM(inventory_Inventory[ReorderPoint]), BLANK())` |

---

### Step 5 — Create Perspectives

In Tabular Editor or the Fabric model properties, create each perspective by selecting which tables and measures to include:

#### Warehouse Operations
- **Tables**: Inventory, Warehouses, InventoryTransactions, Product, ProductCategory
- **Measures**: Total Inventory Value, Available Stock Units, Reserved Stock Units, Units Received, Units Consumed, Products Below Reorder Point
- **Calculation groups**: Time Intelligence, Stock Status View

#### Procurement
- **Tables**: PurchaseOrders, PurchaseOrderItems, Suppliers, ProductSuppliers, Product
- **Measures**: Total PO Value, Open PO Value, PO Fulfillment Rate %, Avg Actual Lead Time Days
- **Calculation groups**: Time Intelligence

#### Supply Chain Risk
- **Tables**: SupplyChainEvents, Suppliers, PurchaseOrders, Product
- **Measures**: Active Disruptions, Active Disruption Revenue Impact, Avg Supplier Reliability

#### Demand Planning
- **Tables**: DemandForecast, Inventory, Warehouses, Product, ProductCategory
- **Measures**: Total Predicted Demand, Avg Forecast Confidence %, Available Stock Units, Products Below Reorder Point
- **Calculation groups**: Time Intelligence

#### Product Catalog
- **Tables**: Product, ProductCategory, ProductSuppliers, Suppliers
- **Measures**: Avg Supplier Reliability, Open PO Value

---

### Step 6 — Recommended Build Order

Follow this sequence to avoid rework:

```
1. ✅ Verify all table relationships are correct in diagram view
2. ✅ Create the Date table and mark it as a Date Table
3. ✅ Build core measures (Step 2) — test each in a simple report visual
4. ✅ Create the Time Intelligence calculation group — test MTD/YTD on one measure
5. ✅ Create the Stock Status calculation group
6. ✅ Create perspectives
7. ✅ Test each perspective in a report connected to that perspective
```

---

## Part 3: Tools You'll Need

| Tool | Purpose | Where to Get It |
|---|---|---|
| **Power BI Desktop** or **Fabric Data Model Editor** | Visual relationship setup, basic measures | Fabric workspace or powerbi.microsoft.com |
| **Tabular Editor 3** (free community edition) | Creating calculation groups and perspectives (not available in PBI Desktop UI by default) | tabulareditor.com |
| **DAX Studio** | Testing and debugging measures with detailed query plans | daxstudio.org |

> **Tip**: Tabular Editor can connect directly to your Fabric workspace semantic model via the **XMLA endpoint** — no need to download files locally. In your Fabric workspace settings, find the XMLA Read/Write endpoint URL and connect from Tabular Editor.

---

## Part 4: Quick Reference — Business Questions This Model Answers

| Business Question | Measure / Table |
|---|---|
| What is total inventory value by warehouse? | `Total Inventory Value` filtered by `Warehouses` |
| Which products are below reorder point? | `Products Below Reorder Point` |
| How much is on open purchase orders? | `Open PO Value` |
| Are suppliers delivering on time? | `Avg Actual Lead Time Days` vs `LeadTimeDays` in Suppliers |
| What supply chain disruptions are active? | `Active Disruptions`, `SupplyChainEvents` table |
| What is the financial exposure from disruptions? | `Active Disruption Revenue Impact` |
| Which categories have the most forecast demand next quarter? | `Total Predicted Demand` filtered by `ForecastDate` and `ProductCategory` |
| How reliable are our forecasts? | `Avg Forecast Confidence %` |
| Which supplier has the best reliability? | `Avg Supplier Reliability` sliced by supplier |
| What is inventory coverage in days? | `Available Stock Units` ÷ recent sales velocity |
