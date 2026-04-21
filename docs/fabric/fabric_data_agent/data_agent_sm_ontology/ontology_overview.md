# Microsoft IQ — Solution Ontology Reference

Details of the `RetailSupplyChainOntologyModel` ontology deployed by this solution.

> ⚠️ **Preview:** Fabric Ontology is in preview. Auto-generation may not bind all properties or create all relationships. Manually verify after generation.
> For general ontology concepts, see the [Ontology Learning Guide](ontology_learning_guide.md).

---

## Ontology Name

**RetailSupplyChainOntologyModel** — auto-generated from the solution's semantic model (`RetailSupplyChainModel`) covering 16 tables across 4 business domains plus a shared date dimension.

---

## Business Domains and Entities

### Product Domain (3 entities)

| Entity | Source Table | Key Column | Description |
|---|---|---|---|
| Product | product.Product | ProductID | Product catalog with names, categories, prices |
| ProductCategory | product.ProductCategory | ProductCategoryID | Category hierarchy |
| ProductLine | product.ProductLine | ProductLineID | Product line groupings |

### Inventory Domain (6 entities)

| Entity | Source Table | Key Column | Description |
|---|---|---|---|
| Warehouses | inventory.Warehouses | WarehouseID | Warehouse locations |
| Inventory | inventory.Inventory | InventoryID | Stock levels by warehouse |
| InventoryTransactions | inventory.InventoryTransactions | TransactionID | Stock movements |
| PurchaseOrders | inventory.PurchaseOrders | PurchaseOrderID | Purchase order headers |
| PurchaseOrderItems | inventory.PurchaseOrderItems | PurchaseOrderItemID | Line items per PO |
| DemandForecast | inventory.DemandForecast | ForecastID | Predicted future demand |

### Supply Chain Domain (4 entities)

| Entity | Source Table | Key Column | Description |
|---|---|---|---|
| Suppliers | supplychain.Suppliers | SupplierID | Supplier directory |
| ProductSuppliers | supplychain.ProductSuppliers | ProductSupplierID | Product-to-supplier mapping (bridge) |
| SupplyChainEvents | supplychain.SupplyChainEvents | EventID | Disruption events |
| SupplyChainEventImpacts | supplychain.SupplyChainEventImpacts | EventImpactID | Impact records per event per supplier |

### Shared Dimension (1 entity)

| Entity | Source Table | Key Column | Description |
|---|---|---|---|
| DimDate | shared.DimDate | FullDate | Calendar date dimension for time intelligence |

---

## Key Relationships

| From Entity | Relationship | To Entity | Join Keys |
|---|---|---|---|
| Product | belongs to | ProductCategory | ProductCategoryID |
| Product | part of | ProductLine | ProductLineID |
| Product | stocked in | Inventory | ProductID |
| Product | tracked in | InventoryTransactions | ProductID |
| Product | forecasted in | DemandForecast | ProductID |
| Product | ordered as | PurchaseOrderItems | ProductID |
| Product | supplied by | ProductSuppliers | ProductID |
| Warehouses | stores | Inventory | WarehouseID |
| Warehouses | logs | InventoryTransactions | WarehouseID |
| Warehouses | receives | DemandForecast | WarehouseID |
| Suppliers | supplies | ProductSuppliers | SupplierID |
| Suppliers | fulfills | PurchaseOrders | SupplierID |
| Suppliers | impacted by | SupplyChainEventImpacts | SupplierID |
| PurchaseOrders | contains | PurchaseOrderItems | PurchaseOrderID |
| SupplyChainEvents | causes | SupplyChainEventImpacts | EventID |
| DimDate | dates | InventoryTransactions | FullDate / TransactionDate |
| DimDate | dates | PurchaseOrders | FullDate / OrderDate |
| DimDate | dates | DemandForecast | FullDate / ForecastDate |

---

## Entity Relationship Map

```
ProductLine <──part of── Product ──belongs to──> ProductCategory
                            │
                            ├──stocked in──> Inventory <──stores── Warehouses
                            │                                         │
                            ├──tracked in──> InventoryTransactions <──logs──┘
                            │                        │
                            ├──forecasted in──> DemandForecast ──dates──> DimDate
                            │
                            ├──ordered as──> PurchaseOrderItems <──contains── PurchaseOrders
                            │                                                     │
                            └──supplied by──> ProductSuppliers <──supplies── Suppliers
                                                                              │
                                              SupplyChainEvents ──causes──> SupplyChainEventImpacts
                                                                              │
                                                                    impacted by──┘
```

---

## Common Query Paths

| Question Type | Entity Path |
|---|---|
| "What products does Contoso supply?" | Suppliers → ProductSuppliers → Product |
| "What's in stock at Main Distribution Center?" | Warehouses → Inventory → Product |
| "Show demand forecast for Tents" | Product → ProductCategory → DemandForecast |
| "Which suppliers had disruptions?" | SupplyChainEvents → SupplyChainEventImpacts → Suppliers |
| "What POs are pending for a supplier?" | Suppliers → PurchaseOrders → PurchaseOrderItems |
| "Show inventory transactions for last month" | DimDate → InventoryTransactions → Product |

---

## Learn More

- [Semantic Model Guide](semantic_model_guide.md) — tables, relationships, and measures to configure
- [Ontology Learning Guide](ontology_learning_guide.md) — general concepts and design patterns
- [Sample Agent Questions](sample_agent_questions.md) — test queries for validation
- [Data Agent Instructions](data_agent_instructions.md) — agent behavior configuration
