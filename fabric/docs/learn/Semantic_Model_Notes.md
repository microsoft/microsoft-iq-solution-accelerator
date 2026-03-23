# Enterprise Semantic Model Blueprint
### For Domains: Customer • Product • Sales • Finance • Inventory • Supply Chain  
### Based on Your Lakehouse + GitHub Raw Data & Schema Definitions

---

# 1. Overview

Your GitHub repo includes:
- **Raw data**  
  `fabric_iq/infra/data/`
- **Schema definitions**  
  `fabric_iq/src/fabric/notebooks/schema/`

You’ve already loaded everything into your Fabric Lakehouse (`gaiyelakehouse`).  
The data is intentionally clean and domain-rich — perfect for building a **proper enterprise semantic model**.

This guide outlines *exactly* what to do next.

---

# 2. Validate Domain Star Schemas

For each domain, confirm you have:

## ✔ Fact Tables (examples)
- `factSales`
- `factInventory`
- `factGL` (finance)
- `factProcurement` or `factSupplyChain`
- `factShipment`
- `factPurchaseOrder`
- `factOrder`

## ✔ Dimension Tables (examples)
- `dimCustomer`
- `dimProduct`
- `dimDate`
- `dimVendor`
- `dimWarehouse`
- `dimRegion`
- `dimEmployee` (if needed for sales reps)

### Recommended Relationship Rules
- Model everything as a **clean star schema**.
- Use **single-direction** (one-direction) relationships from dimension → fact.
- Avoid many-to-many unless required.
- Mark `dimDate` as the **official date table**.
- Hide all surrogate key columns in the model.
- Ensure every fact table has at least:
  - A date key  
  - A product or customer key (or both)

---

# 3. Create Base Business Measures

These foundational measures ensure your calculation groups work consistently.

## Sales Measures
```DAX
Total Sales := SUM(factSales[SalesAmount])
Total Quantity := SUM(factSales[Quantity])
Distinct Customers := DISTINCTCOUNT(factSales[CustomerID])
Avg Selling Price := DIVIDE([Total Sales], [Total Quantity])
``
```







# Your `Order` Table = Sales Fact Table

In star schema design, a **fact table** records *business events*.
 Sales is an event. An *order* is therefore a perfect representation of a sales transaction.

So:

| Business Concept | Your Table     | Semantic Model Role |
| ---------------- | -------------- | ------------------- |
| Sales Orders     | `Order`        | **Fact Table**      |
| Products         | `Product`      | **Dimension**       |
| Customers        | `Customer`     | **Dimension**       |
| Sales Channels   | `SalesChannel` | **Dimension**       |