# Setting Up Table Relationships in Microsoft Fabric Semantic Model

> This guide walks through exactly how to set up the table relationships for the  
> Fabric IQ Supply Chain semantic model in the Microsoft Fabric web interface.

---

## What Are Table Relationships and Why Do They Matter?

A relationship tells the semantic model **how two tables are connected**. Without relationships, tables are isolated — you cannot slice inventory data by product category, or filter purchase orders by warehouse, because the model does not know they are related.

Think of relationships like this:  
- The **Product** table has one row per product  
- The **Inventory** table has many rows — one per product per warehouse  
- The relationship says: "for each product in Product, there can be many rows in Inventory"  
- This is called a **One-to-Many** relationship (written as `1 → *`)

When a user filters by "Camping" in a report, the relationship automatically applies that filter to Inventory, PurchaseOrderItems, DemandForecast, etc.

---

## Key Relationship Concepts Before You Start

### Cardinality (the "type" of relationship)

| Type | Meaning | Example |
|---|---|---|
| **One-to-Many** (1:*) | One row on the left matches many rows on the right | One Product → many Inventory rows |
| **Many-to-One** (*:1) | Same as above, just described from the other direction | Many Inventory rows → one Product |
| **One-to-One** (1:1) | Each row on the left matches exactly one on the right | Rare — usually means tables should be merged |
| **Many-to-Many** (*:*) | Avoid unless necessary — can cause confusing results | Not used in this model |

### Cross-filter Direction

| Setting | Meaning | When to use |
|---|---|---|
| **Single** | Filters flow one way only (from the "one" side to the "many" side) | Default — use for almost everything |
| **Both** | Filters flow in both directions | Only when you specifically need it — can cause performance issues |

**Rule of thumb for this model**: Use **Single** direction for all relationships. The filter always flows from the dimension/reference table (Product, Warehouses, Suppliers) **into** the fact/transaction table (Inventory, InventoryTransactions, PurchaseOrders).

---

## How to Navigate to the Semantic Model in Fabric

1. Go to your **Microsoft Fabric workspace** at [app.fabric.microsoft.com](https://app.fabric.microsoft.com)
2. In the workspace, find your **Semantic Model** item (it has a cube/dataset icon)
3. Click on it to open it
4. In the top menu, click **"Open data model"** — this opens the Model view where you manage relationships

You will see a canvas with all your tables displayed as boxes. If tables are stacked on top of each other, drag them apart to arrange them clearly.

---

## Recommended Canvas Layout

Before creating relationships, arrange your tables in this layout to make the diagram readable:

```
[Top row — Dimension/Reference tables]
  ProductCategory    Product    Warehouses    Suppliers

[Middle row — Bridge/Mapping tables]
  ProductSuppliers    SupplyChainEvents

[Bottom row — Fact/Transaction tables]
  Inventory    InventoryTransactions    PurchaseOrders    PurchaseOrderItems    DemandForecast
```

This layout visually shows that filters flow **downward** from reference tables into transactional tables.

---

## How to Create a Relationship — Step by Step

There are two ways to create a relationship in Fabric:

### Method A — Drag and Drop (Easiest)

1. On the canvas, find the **source table** (the "one" side — e.g., `Product`)
2. Click and hold the **field you want to join on** (e.g., `ProductID`)
3. Drag it onto the **destination table** (the "many" side — e.g., `Inventory`)
4. Drop it on the matching field (e.g., `ProductID`)
5. A line appears between the tables — the relationship is created
6. Verify the settings in the panel that appears (see "Verify Your Settings" below)

### Method B — Manual Dialog (More Control)

1. In the top menu, click **"Manage relationships"**
2. Click **"New relationship"**
3. In the dialog:
   - **From table**: select the "one" side table (e.g., `product_Product`)
   - **From column**: select the join field (e.g., `ProductID`)
   - **To table**: select the "many" side table (e.g., `inventory_Inventory`)
   - **To column**: select the matching field (e.g., `ProductID`)
   - **Cardinality**: select `One to many (1:*)`
   - **Cross filter direction**: select `Single`
   - **Make this relationship active**: check this box ✅
4. Click **Confirm**

### Verify Your Settings

After creating each relationship, click on the line between tables to verify:
- The `1` symbol appears on the Product/Warehouse/Supplier side
- The `*` symbol appears on the Inventory/Transaction side
- The arrow points from `1` toward `*`

---

## All Relationships to Create

Work through this list one relationship at a time. The **From** column is always the "one" side (the reference/dimension table).

### Group 1: Product → Inventory Domain

| # | From Table | From Field | To Table | To Field | Cardinality | Direction |
|---|---|---|---|---|---|---|
| 1 | `product_Product` | `ProductID` | `inventory_Inventory` | `ProductID` | One to Many | Single |
| 2 | `product_Product` | `ProductID` | `inventory_InventoryTransactions` | `ProductID` | One to Many | Single |
| 3 | `product_Product` | `ProductID` | `inventory_PurchaseOrderItems` | `ProductID` | One to Many | Single |
| 4 | `product_Product` | `ProductID` | `inventory_DemandForecast` | `ProductID` | One to Many | Single |
| 5 | `product_ProductCategory` | `CategoryID` | `product_Product` | `ProductCategoryID` | One to Many | Single |

---

### Group 2: Warehouses → Inventory Domain

| # | From Table | From Field | To Table | To Field | Cardinality | Direction |
|---|---|---|---|---|---|---|
| 6 | `inventory_Warehouses` | `WarehouseID` | `inventory_Inventory` | `WarehouseLocation` | One to Many | Single |
| 7 | `inventory_Warehouses` | `WarehouseID` | `inventory_InventoryTransactions` | `WarehouseLocation` | One to Many | Single |
| 8 | `inventory_Warehouses` | `WarehouseID` | `inventory_PurchaseOrders` | `DeliveryLocation` | One to Many | Single |

> **Note**: `WarehouseID` values in your data are `Main`, `Backup`, `Regional`. The `WarehouseLocation` and `DeliveryLocation` fields in the other tables use these same values as foreign keys.

---

### Group 3: Purchase Orders → Line Items

| # | From Table | From Field | To Table | To Field | Cardinality | Direction |
|---|---|---|---|---|---|---|
| 9 | `inventory_PurchaseOrders` | `PurchaseOrderID` | `inventory_PurchaseOrderItems` | `PurchaseOrderID` | One to Many | Single |

---

### Group 4: Suppliers → Supply Chain Domain

| # | From Table | From Field | To Table | To Field | Cardinality | Direction |
|---|---|---|---|---|---|---|
| 10 | `supplychain_Suppliers` | `SupplierID` | `inventory_PurchaseOrders` | `SupplierID` | One to Many | Single |
| 11 | `supplychain_Suppliers` | `SupplierID` | `supplychain_ProductSuppliers` | `SupplierID` | One to Many | Single |
| 12 | `supplychain_Suppliers` | `SupplierID` | `supplychain_SupplyChainEvents` | `SupplierID` | One to Many | Single |

> **Note**: `SupplyChainEvents.SupplierID` can be NULL (for general/market-wide events). This is fine — the relationship still works. NULL rows simply won't match any supplier and will appear as "blank" in reports.

---

### Group 5: Product → Supply Chain Domain

| # | From Table | From Field | To Table | To Field | Cardinality | Direction |
|---|---|---|---|---|---|---|
| 13 | `product_Product` | `ProductID` | `supplychain_ProductSuppliers` | `ProductID` | One to Many | Single |

---

## Complete Relationship Diagram

After all 13 relationships are created, your model diagram should look like this:

```
ProductCategory ──→ Product ──→ Inventory
                      │    ──→ InventoryTransactions
                      │    ──→ PurchaseOrderItems
                      │    ──→ DemandForecast
                      └──→ ProductSuppliers ←── Suppliers ──→ SupplyChainEvents
                                                    │
Warehouses ──→ Inventory                            └──→ PurchaseOrders ──→ PurchaseOrderItems
         ──→ InventoryTransactions
         ──→ PurchaseOrders
```

---

## How to Check Your Relationships for Problems

### Check 1: Look for missing relationship lines
On the canvas, every table should have at least one line connecting it to another table. If any table is floating with no connections, it is isolated and will not filter correctly.

### Check 2: Verify the 1 and * symbols
Click on each relationship line. Confirm:
- `1` is on the dimension/reference side (Product, Warehouses, Suppliers, ProductCategory)
- `*` is on the fact/transaction side (Inventory, InventoryTransactions, PurchaseOrders, etc.)

If you see `*` on both sides, the relationship is Many-to-Many — this usually means the join field has duplicate values on the "one" side. Check that `ProductID` in `Product` is unique (no duplicate rows).

### Check 3: Check for inactive relationships
An **inactive relationship** appears as a **dashed line** instead of a solid line. Inactive relationships are not used by default. If you see a dashed line, click it and check the "Make this relationship active" setting.

### Check 4: Run a quick test in a report
Create a simple Matrix visual:
- Rows: `ProductCategory` from `product_ProductCategory`
- Values: `CurrentStock` from `inventory_Inventory`

If the relationship is working, you should see stock totals broken down by Camping, Kitchen, and Ski. If all stock appears in a single "blank" row, the relationship between Product and Inventory is not working correctly.

---

## Troubleshooting Common Problems

### Problem: "A relationship already exists between these tables"
**Cause**: You already created this relationship, or Fabric auto-detected it.  
**Fix**: Click "Manage relationships" to review existing relationships and avoid duplicates.

### Problem: The `*` symbol appears on the wrong side
**Cause**: The field you chose as the "one" side has duplicate values (not truly unique).  
**Fix**: Check that `ProductID` in `product_Product` has no duplicate rows. Run this in the lakehouse SQL endpoint:
```sql
SELECT ProductID, COUNT(*) AS cnt
FROM product.Product
GROUP BY ProductID
HAVING COUNT(*) > 1
```
If any rows are returned, there are duplicates that need to be resolved.

### Problem: Warehouse relationship not working (`WarehouseID` → `WarehouseLocation`)
**Cause**: The values may not match exactly — e.g., `"Main"` vs `"main"` (case difference) or trailing spaces.  
**Fix**: Check the actual values with:
```sql
SELECT DISTINCT WarehouseID FROM inventory.Warehouses
SELECT DISTINCT WarehouseLocation FROM inventory.Inventory
```
Both should return exactly: `Main`, `Backup`, `Regional`.

### Problem: SupplierID relationship shows many blank rows
**Cause**: `SupplyChainEvents.SupplierID` is NULL for general events (expected behavior).  
**Fix**: This is normal. In reports, use a filter to exclude blank suppliers when you only want supplier-specific events.

### Problem: Relationship line is dashed (inactive)
**Cause**: Fabric allows only one active relationship between two tables. If you accidentally created two relationships between the same tables, the second one becomes inactive.  
**Fix**: Go to "Manage relationships", find the duplicate, and delete it.

---

## After All Relationships Are Set

Once all 13 relationships are in place:

1. **Save the model** — click Save in the top right
2. **Proceed to Step 2** of the semantic model guide: building your core measures
3. Reference file: [supplychain_semantic_model_extra.md](supplychain_semantic_model_extra.md)

---

## Quick Reference Checklist

Use this checklist to confirm all relationships are created:

- [ ] ProductCategory → Product (CategoryID → ProductCategoryID)
- [ ] Product → Inventory (ProductID → ProductID)
- [ ] Product → InventoryTransactions (ProductID → ProductID)
- [ ] Product → PurchaseOrderItems (ProductID → ProductID)
- [ ] Product → DemandForecast (ProductID → ProductID)
- [ ] Product → ProductSuppliers (ProductID → ProductID)
- [ ] Warehouses → Inventory (WarehouseID → WarehouseLocation)
- [ ] Warehouses → InventoryTransactions (WarehouseID → WarehouseLocation)
- [ ] Warehouses → PurchaseOrders (WarehouseID → DeliveryLocation)
- [ ] PurchaseOrders → PurchaseOrderItems (PurchaseOrderID → PurchaseOrderID)
- [ ] Suppliers → PurchaseOrders (SupplierID → SupplierID)
- [ ] Suppliers → ProductSuppliers (SupplierID → SupplierID)
- [ ] Suppliers → SupplyChainEvents (SupplierID → SupplierID)

**Total: 13 relationships, all One-to-Many, Single direction**
