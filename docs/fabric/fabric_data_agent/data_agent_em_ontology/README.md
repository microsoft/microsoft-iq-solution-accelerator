# Entity Model Ontology — Fabric Data Agent Guide

This guide explains how to manually create a Microsoft Fabric Data Agent using an **Entity Model Ontology** built on top of a Fabric Lakehouse. This is **Alternative 1** from the [Fabric Data Agent overview](../README.md).

> **Note:** Our deployment script does **not** create this data agent automatically. Follow the steps below to set it up manually.

---

## What Is an Entity Model Ontology?

A Microsoft Fabric Ontology defines a semantic layer over your lakehouse data. The **Entity Model** approach lets you:

- Define **entities** (e.g., Product, Inventory, Supplier) that map to lakehouse tables or views
- Define **relationships** between entities (e.g., Product → Inventory, Supplier → PurchaseOrder)
- Surface that structured semantic model as a data source for a Fabric Data Agent

The data agent uses the ontology to translate natural language questions into structured queries against the lakehouse.

---

## Prerequisites

- A Microsoft Fabric workspace with a deployed lakehouse (`miqdata` or equivalent)
- Contributor or higher permissions on the workspace
- Lakehouse tables loaded (all 22 Delta tables across 6 domain schemas)

---

## Steps to Create the Fabric Data Agent

### Step 1 — Create a Fabric Ontology

1. In your Fabric workspace, select **New item**.
2. Search for **Ontology** and select it.
3. Name it, for example, `ontology_entity_model`.
4. Open the ontology editor.

### Step 2 — Build the Entity Model

Add the following entities by connecting them to the corresponding lakehouse tables.

| Entity Name | Lakehouse Table | Domain |
|---|---|---|
| Product | product.Product | Product |
| ProductCategory | product.ProductCategory | Product |
| Inventory | inventory.Inventory | Inventory |
| InventoryTransactions | inventory.InventoryTransactions | Inventory |
| Warehouse | inventory.Warehouses | Inventory |
| PurchaseOrder | inventory.PurchaseOrders | Inventory |
| PurchaseOrderItems | inventory.PurchaseOrderItems | Inventory |
| DemandForecast | inventory.DemandForecast | Inventory |
| Supplier | supplychain.Suppliers | Supply Chain |
| ProductSuppliers | supplychain.ProductSuppliers | Supply Chain |
| SupplyChainEvents | supplychain.SupplyChainEvents | Supply Chain |
| Customer | customer.Customer | Customer |
| Order | sales.Order | Sales |
| OrderLine | sales.OrderLine | Sales |

For each entity, select the key fields you want the agent to query. Avoid exposing raw GUID/ID-only fields unless they are needed for joins.

### Step 3 — Define Relationships

Add the following relationships in the ontology editor:

```
Product ──< Inventory                  (ProductId)
Product ──< InventoryTransactions      (ProductId)
Product ──< DemandForecast             (ProductId)
Product ──< PurchaseOrderItems         (ProductId)
Warehouse ──< Inventory                (WarehouseId)
Warehouse ──< PurchaseOrders           (WarehouseId)
PurchaseOrder ──< PurchaseOrderItems   (PurchaseOrderId)
Supplier ──< ProductSuppliers          (SupplierId)
Product ──< ProductSuppliers           (ProductId)
Supplier ──< SupplyChainEvents         (SupplierId)
Customer ──< Order                     (CustomerId)
Order ──< OrderLine                    (OrderId)
```

### Step 4 — Create the Fabric Data Agent

1. In your Fabric workspace, select **New item**.
2. Search for **Data Agent** and select **Fabric Data Agent**.
3. Name it, for example, `data_agent_em_ontology`.
4. Under **Data sources**, select **Ontology** and choose `ontology_entity_model`.
5. Save the data agent.

### Step 5 — Add Agent Instructions

Paste agent instructions into the **Agent Instructions** field of the data agent. See [sample_agent_questions.md](sample_agent_questions.md) for validation questions you can use after setup.

Recommended instruction principles:
- Reference entities by their ontology name (e.g., `Inventory`, `DemandForecast`), not raw table paths
- Instruct the agent to return human-readable names alongside keys
- Instruct the agent to use only data available in the ontology — never invent values
- For time-based questions, instruct the agent to filter using date fields available in the ontology (e.g., `ForecastDate`, `OrderDate`, `TransactionDate`)

---

## 📁 Files in This Folder

| File | Purpose |
|---|---|
| [README.md](README.md) | This guide — setup instructions for the entity model ontology agent |
| [sample_agent_questions.md](sample_agent_questions.md) | Sample test questions to validate the agent after setup |

---

## Date and Time Queries

The Fabric Data Agent does **not** have access to a live system clock. For questions involving "today" or "current date":

- Use a date field from the ontology as the reference (e.g., `ForecastDate`, `TransactionDate`)
- Or filter explicitly: _"What is the demand forecast for Tents for May 2026?"_
- Avoid relying on the agent to infer the current date from model memory

---

## Testing the Agent

Once set up, use the questions in [sample_agent_questions.md](sample_agent_questions.md) to validate the agent across these domains:

- **Inventory** — stock levels, reorder points, warehouse capacity
- **Supply Chain** — supplier list, purchase orders, disruption events
- **Demand Forecast** — predicted demand by product category and period
- **Product** — product catalog, categories, pricing

---

## Customization Tips

- Add more entities to the ontology as new lakehouse tables are introduced
- Refine relationship paths if the agent returns incorrect join results
- Add calculated fields or measures in the ontology to support common aggregations (e.g., available stock = CurrentStock − ReservedStock)
- Update agent instructions to reflect any domain terminology specific to your organization

