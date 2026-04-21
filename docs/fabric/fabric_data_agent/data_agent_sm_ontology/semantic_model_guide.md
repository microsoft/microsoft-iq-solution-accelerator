# Semantic Model Guide

This guide explains how to create and configure the semantic model that powers the ontology-based Fabric Data Agent.

---

## What Is a Semantic Model?

A [Fabric Semantic Model](https://learn.microsoft.com/fabric/get-started/direct-lake-overview) sits between the lakehouse and the ontology. It defines:

- **Which tables** are included
- **How tables relate** to each other (relationships)
- **What measures** are available (aggregations, calculations)
- **Display-friendly names** for columns and tables

The ontology is generated *from* this model — so getting it right here means better answers from the data agent.

---

## Tables to Include

Include all 22 tables across the 6 domain schemas:

| Domain | Tables |
|---|---|
| **Customer** | Customer, CustomerRelationshipType, CustomerTradeName, Location, CustomerAccount |
| **Product** | Product, ProductCategory |
| **Sales** | Order, OrderLine, OrderPayment |
| **Finance** | Invoice, Account, Payment |
| **Inventory** | Warehouses, Inventory, InventoryTransactions, PurchaseOrders, PurchaseOrderItems, DemandForecast |
| **Supply Chain** | Suppliers, ProductSuppliers, SupplyChainEvents |

**Optional:** Add a `DimDate` shared dimension table for time intelligence queries.

---

## Relationships to Define

Define these relationships in the semantic model editor. Use the primary/foreign key pairs shown.

### Customer Domain

```
CustomerRelationshipType (1) ──> Customer (*)     on CustomerRelationshipTypeId
Customer (1) ──> Location (*)                      on CustomerId
Customer (1) ──> CustomerAccount (*)               on CustomerId
Customer (1) ──> CustomerTradeName (*)              on CustomerId
```

### Product Domain

```
ProductCategory (1) ──> Product (*)                on CategoryId / ProductCategoryID
```

### Sales Domain

```
Customer (1) ──> Order (*)                         on CustomerId
Order (1) ──> OrderLine (*)                        on OrderId
Order (1) ──> OrderPayment (*)                     on OrderId
Product (1) ──> OrderLine (*)                      on ProductId
```

### Finance Domain

```
Customer (1) ──> Invoice (*)                       on CustomerId
Customer (1) ──> Account (*)                       on CustomerId
Invoice (1) ──> Payment (*)                        on InvoiceId
```

### Inventory Domain

```
Warehouses (1) ──> Inventory (*)                   on WarehouseId
Product (1) ──> Inventory (*)                      on ProductId
Product (1) ──> InventoryTransactions (*)           on ProductId
Product (1) ──> DemandForecast (*)                 on ProductId
Product (1) ──> PurchaseOrderItems (*)             on ProductId
PurchaseOrders (1) ──> PurchaseOrderItems (*)      on PurchaseOrderId
```

### Supply Chain Domain

```
Suppliers (1) ──> ProductSuppliers (*)             on SupplierId
Product (1) ──> ProductSuppliers (*)               on ProductId
Suppliers (1) ──> SupplyChainEvents (*)            on SupplierId
```

---

## Measures to Add

Dimension tables with no numeric columns may be **skipped** during ontology generation. Add a simple measure to prevent this.

| Table | Measure | DAX Expression |
|---|---|---|
| ProductCategory | CategoryCount | `COUNTROWS('ProductCategory')` |
| CustomerRelationshipType | RelTypeCount | `COUNTROWS('CustomerRelationshipType')` |
| Warehouses | WarehouseCount | `COUNTROWS('Warehouses')` |
| Suppliers | SupplierCount | `COUNTROWS('Suppliers')` |

### Useful business measures (optional)

| Measure | DAX Expression |
|---|---|
| TotalRevenue | `SUMX('OrderLine', [LineTotal])` |
| TotalOrders | `COUNTROWS('Order')` |
| AvgOrderValue | `AVERAGEX('Order', [OrderTotal])` |
| GrossMarginPct | `DIVIDE(SUM('OrderLine'[LineTotal]) - SUM('OrderLine'[StandardCost]), SUM('OrderLine'[LineTotal]))` |

---

## Storage Mode

Choose **DirectLake** mode (the default for Fabric semantic models). This keeps data in OneLake without import, providing:

- Real-time data access
- No refresh scheduling needed
- Lower memory usage

> **Important:** DirectLake requires all relationships to be explicitly defined. It will not infer join paths.

---

## Common Issues

| Issue | Cause | Fix |
|---|---|---|
| Table missing from ontology | No numeric measure on the table | Add a `COUNTROWS` measure |
| Relationship not working | Relationship direction wrong or missing | Verify cardinality and key columns in the model editor |
| Duplicate column names across tables | Causes type conflicts in ontology | Rename columns to be globally unique (e.g., `WarehouseStatus` vs `OrderStatus`) |

---

## Next Steps

After creating the semantic model:

1. **Create the ontology** — see [README.md](README.md), Step 2
2. **Review the ontology** — see [ontology_overview.md](ontology_overview.md)
3. **Configure the data agent** — see [data_agent_instructions.md](data_agent_instructions.md)
