# Microsoft IQ — Solution Ontology Reference

Details of the `RetailSupplyChainOntologyModel` ontology deployed by this solution.

> ⚠️ **Preview:** Fabric Ontology is in preview. Auto-generation may not bind all properties or create all relationships. Manually verify after generation.
> For general ontology concepts, see the [Ontology Learning Guide](ontology_learning_guide.md).

---

## Ontology Name

**RetailSupplyChainOntologyModel** — auto-generated from the solution's semantic model covering 22 tables across 6 business domains.

---

## Business Domains and Entities

### Customer Domain (5 entities)

| Entity | Source Table | Key Column | Description |
|---|---|---|---|
| Customer | customer.Customer | CustomerID | Customer master records |
| CustomerRelationshipType | customer.CustomerRelationshipType | RelationshipTypeID | Relationship classifications |
| CustomerTradeName | customer.CustomerTradeName | TradeNameID | Trade name aliases |
| Location | customer.Location | LocationID | Customer locations |
| CustomerAccount | customer.CustomerAccount | AccountID | Account details |

### Product Domain (2 entities)

| Entity | Source Table | Key Column | Description |
|---|---|---|---|
| Product | product.Product | ProductID | Product catalog with names, categories, prices |
| ProductCategory | product.ProductCategory | CategoryID | Category hierarchy |

### Sales Domain (3 entities)

| Entity | Source Table | Key Column | Description |
|---|---|---|---|
| Order | sales.Order | OrderID | Sales order headers |
| OrderLine | sales.OrderLine | OrderLineID | Line items per order |
| OrderPayment | sales.OrderPayment | PaymentID | Payment records |

### Finance Domain (3 entities)

| Entity | Source Table | Key Column | Description |
|---|---|---|---|
| Invoice | finance.Invoice | InvoiceID | Invoice records |
| Account | finance.Account | AccountID | Financial accounts |
| Payment | finance.Payment | PaymentID | Payment transactions |

### Inventory Domain (5 entities)

| Entity | Source Table | Key Column | Description |
|---|---|---|---|
| Warehouses | inventory.Warehouses | WarehouseID | Warehouse locations |
| Inventory | inventory.Inventory | InventoryID | Stock levels by warehouse |
| InventoryTransactions | inventory.InventoryTransactions | TransactionID | Stock movements |
| PurchaseOrders | inventory.PurchaseOrders | PurchaseOrderID | Purchase order headers |
| PurchaseOrderItems | inventory.PurchaseOrderItems | PurchaseOrderItemID | Line items per PO |
| DemandForecast | inventory.DemandForecast | ForecastID | Predicted future demand |

### Supply Chain Domain (3 entities)

| Entity | Source Table | Key Column | Description |
|---|---|---|---|
| Suppliers | supplychain.Suppliers | SupplierID | Supplier directory |
| ProductSuppliers | supplychain.ProductSuppliers | ProductSupplierID | Product-to-supplier mapping (bridge) |
| SupplyChainEvents | supplychain.SupplyChainEvents | EventID | Disruption events |

---

## Key Relationships

| From Entity | Relationship | To Entity | Join Keys |
|---|---|---|---|
| Order | contains | OrderLine | OrderID |
| Order | paid via | OrderPayment | OrderID |
| Product | categorized as | ProductCategory | CategoryID |
| Product | stocked in | Inventory | ProductID |
| Product | supplied by | ProductSuppliers | ProductID |
| Suppliers | supplies | ProductSuppliers | SupplierID |
| Warehouses | stores | Inventory | WarehouseID |
| PurchaseOrders | contains | PurchaseOrderItems | PurchaseOrderID |
| Suppliers | fulfills | PurchaseOrders | SupplierID |
| Product | forecasted in | DemandForecast | ProductID |
| Customer | has | CustomerAccount | CustomerID |
| Customer | located at | Location | CustomerID |
| SupplyChainEvents | affects | Suppliers | SupplierID |

---

## Entity Relationship Map

```
Customer ──has──> CustomerAccount
    │
    └──located at──> Location

Product ──categorized as──> ProductCategory
    │
    ├──stocked in──> Inventory <──stores── Warehouses
    │
    ├──supplied by──> ProductSuppliers <──supplies── Suppliers
    │                                                    │
    │                                      fulfills──> PurchaseOrders ──contains──> PurchaseOrderItems
    │
    └──forecasted in──> DemandForecast

Order ──contains──> OrderLine
    └──paid via──> OrderPayment

SupplyChainEvents ──affects──> Suppliers
```

---

## Common Query Paths

| Question Type | Entity Path |
|---|---|
| "What products does Contoso supply?" | Suppliers → ProductSuppliers → Product |
| "What's in stock at Main Distribution Center?" | Warehouses → Inventory → Product |
| "Show demand forecast for Tents" | Product → ProductCategory → DemandForecast |
| "Which suppliers had disruptions?" | SupplyChainEvents → Suppliers |
| "List orders with payments" | Order → OrderLine + Order → OrderPayment |
| "What POs are pending for a supplier?" | Suppliers → PurchaseOrders → PurchaseOrderItems |

---

## Learn More

- [Semantic Model Guide](semantic_model_guide.md) — tables, relationships, and measures to configure
- [Ontology Learning Guide](ontology_learning_guide.md) — general concepts and design patterns
- [Sample Agent Questions](sample_agent_questions.md) — test queries for validation
- [Data Agent Instructions](data_agent_instructions.md) — agent behavior configuration
