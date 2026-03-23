# Semantic Model Relationship Setup Guide

This guide shows how to connect your existing Fabric Lakehouse tables into a clean semantic model.
No table renaming required.

---

## 1. Fact vs Dimension Tables

### Dimensions
- product
- productcategory
- warehouses
- suppliers

### Fact Tables
- inventory
- inventorytransactions
- demandforecast
- purchaseorders
- purchaseorderitems
- supplychainevents
- productsuppliers (bridge or fact depending on use-case)

---

## 2. Required Relationships (Create in Model View)

### Product Domain
productcategory[ProductCategoryID] → product[ProductCategoryID]  
product[ProductID] → inventory[ProductID]  
product[ProductID] → inventorytransactions[ProductID]  
product[ProductID] → purchaseorderitems[ProductID]  
product[ProductID] → demandforecast[ProductID]

### Supplier Domain
suppliers[SupplierID] → purchaseorders[SupplierID]  
purchaseorders[PurchaseOrderID] → purchaseorderitems[PurchaseOrderID]  
suppliers[SupplierID] → productsuppliers[SupplierID]  
suppliers[SupplierID] → supplychainevents[SupplierID]  (if column exists)

### Warehouse Domain
warehouses[WarehouseID] → inventory[WarehouseID]  
warehouses[WarehouseID] → inventorytransactions[WarehouseID]

### Date Table (your global date dimension)
Date[Date] → inventory[SnapshotDate]  
Date[Date] → inventorytransactions[TransactionDate]  
Date[Date] → purchaseorders[OrderDate]  
Date[Date] → demandforecast[ForecastDate]  
Date[Date] → supplychainevents[EventDate]

**Always use:**
- Relationship type: Many-to-One
- Cross-filter direction: Single
- Direction: Dimension → Fact

---

## 3. Hide These Columns (Cleaner Model)

Hide all keys and foreign keys:
- ProductID  
- ProductCategoryID  
- WarehouseID  
- SupplierID  
- PurchaseOrderID  
- PurchaseOrderItemID  
- ForecastID  
- TransactionID  
- EventID  

---

## 4. Basic Measures to Create

Total Inventory :=
SUM(inventory[QuantityOnHand])

Inventory Value :=
SUM(inventory[InventoryValue])

Inventory Movements :=
SUM(inventorytransactions[Quantity])

PO Amount :=
SUM(purchaseorderitems[LineAmount])

Forecast Quantity :=
SUM(demandforecast[ForecastQty])

Supply Chain Events :=
COUNTROWS(supplychainevents)

---

## 5. Final Checklist

- All relationships created (dimension → fact only)
- All relationships set to single direction
- Date table marked as date table
- Keys + foreign keys hidden
- At least a few basic measures created
- Matrix visual test (Product × Warehouse × Total Inventory)

You now have a clean, maintainable semantic model.