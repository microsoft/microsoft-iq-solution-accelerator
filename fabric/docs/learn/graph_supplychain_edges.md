# Fabric Ontology Graph Edges — Product, Inventory & Supply Chain Schemas

## Overview

This document lists all recommended edges (relationships) to define in the Fabric Ontology Graph Model for the `product`, `inventory`, and `supplychain` schemas.

Schemas loaded: **product**, **inventory**, **supplychain**

---

## Within `product` Schema

| # | Edge Name | From Entity | To Entity | From Column | To Column | Cardinality |
|---|---|---|---|---|---|---|
| 1 | BelongsToCategory | `Product` | `ProductCategory` | `ProductCategoryID` | `CategoryID` | Many → One |
| 2 | HasSubCategory | `ProductCategory` | `ProductCategory` | `ParentCategoryID` | `CategoryID` | Many → One (self-ref) |

---

## Within `inventory` Schema

| # | Edge Name | From Entity | To Entity | From Column | To Column | Cardinality |
|---|---|---|---|---|---|---|
| 3 | StoredAt | `Inventory` | `Warehouses` | `WarehouseLocation` | `WarehouseID` | Many → One |
| 4 | ProcessedAt | `InventoryTransactions` | `Warehouses` | `WarehouseLocation` | `WarehouseID` | Many → One |
| 5 | DeliveredTo | `PurchaseOrders` | `Warehouses` | `DeliveryLocation` | `WarehouseID` | Many → One |
| 6 | Contains | `PurchaseOrders` | `PurchaseOrderItems` | `PurchaseOrderID` | `PurchaseOrderID` | One → Many |

---

## Cross-Schema: `inventory` → `product`

| # | Edge Name | From Entity | To Entity | From Column | To Column | Cardinality |
|---|---|---|---|---|---|---|
| 7 | TracksProduct | `Inventory` | `Product` | `ProductID` | `ProductID` | Many → One |
| 8 | AffectsProduct | `InventoryTransactions` | `Product` | `ProductID` | `ProductID` | Many → One |
| 9 | OrdersProduct | `PurchaseOrderItems` | `Product` | `ProductID` | `ProductID` | Many → One |
| 10 | ForecastsProduct | `DemandForecast` | `Product` | `ProductID` | `ProductID` | Many → One |

---

## Cross-Schema: `inventory` → `supplychain`

| # | Edge Name | From Entity | To Entity | From Column | To Column | Cardinality |
|---|---|---|---|---|---|---|
| 11 | OrderedFrom | `PurchaseOrders` | `Suppliers` | `SupplierID` | `SupplierID` | Many → One |

---

## Within + Across `supplychain`

| # | Edge Name | From Entity | To Entity | From Column | To Column | Cardinality |
|---|---|---|---|---|---|---|
| 12 | HasBackupSupplier | `Suppliers` | `Suppliers` | `PrimarySupplierID` | `SupplierID` | Many → One (self-ref) |
| 13 | SuppliedBy | `ProductSuppliers` | `Suppliers` | `SupplierID` | `SupplierID` | Many → One |
| 14 | SupplierForProduct | `ProductSuppliers` | `Product` | `ProductID` | `ProductID` | Many → One |
| 15 | AffectsSupplier | `SupplyChainEvents` | `Suppliers` | `SupplierID` | `SupplierID` | Many → One (nullable) |

---

## Summary — 15 Edges Total

| Scope | Count |
|---|---|
| Within `product` | 2 |
| Within `inventory` | 4 |
| `inventory` → `product` (cross-schema) | 4 |
| `inventory` → `supplychain` (cross-schema) | 1 |
| Within/across `supplychain` | 4 |
| **Total** | **15** |

---

## Priority Edges for Data Agent Query Quality

These cross-schema edges are the most impactful — they enable multi-domain natural language questions:

1. **OrderedFrom** (`PurchaseOrders` → `Suppliers`) — *"Which suppliers have pending orders?"*
2. **TracksProduct** (`Inventory` → `Product`) — *"Which products are low in stock?"*
3. **SupplierForProduct** (`ProductSuppliers` → `Product`) — *"Which products does Supplier X supply?"*
4. **AffectsSupplier** (`SupplyChainEvents` → `Suppliers`) — *"Which suppliers are affected by active disruptions?"*
5. **Contains** (`PurchaseOrders` → `PurchaseOrderItems`) — *"What items are on a given purchase order?"*

---

## Notes

- `WarehouseLocation` in `Inventory` and `InventoryTransactions` uses `WarehouseID` as its value — name is misleading but confirms FK relationship.
- `SupplierID` in `SupplyChainEvents` is **nullable** (NULL for general/industry-wide events) — mark this edge as optional in the ontology.
- `PrimarySupplierID` in `Suppliers` is NULL for primary suppliers — self-referencing edge applies only to Backup/Emergency supplier rows.
- `ProductSuppliers` acts as a **junction/bridge entity** connecting both `product` and `supplychain` schemas.
