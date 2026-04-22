# Power BI Dashboards

This folder documents the Power BI reports shipped with the Microsoft IQ Solution Accelerator. The `.pbix` files live under [`src/fabric/dashboards/`](../../../src/fabric/dashboards/) and are intended to be published to the Microsoft Fabric workspace created by the accelerator (see [`DeploymentGuideFabric.md`](../DeploymentGuideFabric.md)).

Two reports are provided:

| Report | File | Focus |
|---|---|---|
| Sales Overview | [`Sales Overview.pbix`](../../../src/fabric/dashboards/Sales%20Overview.pbix) | Net sales, revenue, product and customer segmentation |
| Supply Chain Management | [`Supply Chain Management.pbix`](../../../src/fabric/dashboards/Supply%20Chain%20Management.pbix) | Inventory health, warehouse utilization, procurement, supplier performance |

Both reports are built on the lakehouse tables created by the schema notebooks in [`src/fabric/notebooks/schema/`](../../../src/fabric/notebooks/schema/). For the complete table inventory see [`schema_and_tables.md`](../../../src/fabric/notebooks/schema/schema_and_tables.md).

---

## 1. Sales Overview

**File:** [`src/fabric/dashboards/Sales Overview.pbix`](../../../src/fabric/dashboards/Sales%20Overview.pbix)

A single-page executive summary of sales performance across product lines, categories, and customer segments.

### Page: Sales Overview

Key visuals and their purpose:

| Visual | Type | Purpose |
|---|---|---|
| Net Sales | Card | Headline net sales KPI for the selected period |
| YoY Net Sales Comparison | Area / line chart | Year-over-year trend of net sales |
| Top 5 Selling Products by Quantity | Clustered bar chart | Best-selling SKUs measured by units sold |
| Top 5 Selling Products by Revenue | Clustered bar chart | Best-selling SKUs measured by revenue |
| Sales Distribution by Category | Donut chart | Mix of net sales across product categories / product lines |
| Revenue Distribution by Customer Segment | Donut / column chart | Revenue mix across customer types |
| Time / category slicers | Slicer | Filter by Year, Month, Product Line, Customer Type |

### Data sources

Backed by the `sales`, `product`, and `customer` lakehouse schemas:

- `sales.Order`, `sales.OrderLine` — order headers and line items (quantity, net sales, revenue)
- `product.Product`, `product.ProductCategory`, `product.ProductLine` — product hierarchy
- `customer.Customer` — customer type segmentation

### Typical questions answered

- What are our total net sales and how do they compare year over year?
- Which products drive the most units and the most revenue?
- How is revenue distributed across product lines and customer segments?
- How do sales trend by month within a given year?

---

## 2. Supply Chain Management

**File:** [`src/fabric/dashboards/Supply Chain Management.pbix`](../../../src/fabric/dashboards/Supply%20Chain%20Management.pbix)

A single-page operational view of inventory, warehouse capacity, procurement, and supplier performance.

### Page: Supply Chain Overview

Key visuals and their purpose:

| Visual | Type | Purpose |
|---|---|---|
| Total Stock on Hand | Card | Current inventory quantity across warehouses |
| Avg Warehouse Utilization | Card | Average capacity utilization across warehouses |
| Total Procurement Value | Card | Aggregate value of purchase orders |
| Supplier Avg Reliability Score | Card | Portfolio-level supplier reliability |
| Inventory Health at a Glance | Column / bar chart | Stock health status breakdown (e.g., healthy, low, overstocked) |
| Procurement Trend Analysis | Line & clustered column combo | Purchase order value and volume over time |
| Warehouse Capacity | Clustered bar chart | Per-warehouse capacity utilization |
| Top 5 Product Profitability Analysis | Clustered column chart | Margin view using list price vs. standard cost |
| Supplier Performance Matrix | Scatter chart | Reliability vs. risk / lead time across suppliers |
| Category / time / supplier slicers | Slicer | Filter by Year, Month, Product Line, Supplier Type, Warehouse |

### Data sources

Backed by the `inventory`, `supplychain`, and `product` lakehouse schemas:

- `inventory.Inventory`, `inventory.InventoryTransactions` — stock levels and movement history
- `inventory.Warehouses` — warehouse master data and capacity utilization
- `inventory.PurchaseOrders`, `inventory.PurchaseOrderItems` — procurement activity
- `supplychain.Suppliers`, `supplychain.ProductSuppliers` — supplier master data and product mapping, including reliability, risk, and lead-time metrics
- `product.Product`, `product.ProductCategory` — product hierarchy and cost/price for profitability

### Typical questions answered

- How much stock do we currently hold and how healthy is it?
- How well are our warehouses utilized, and which ones are near capacity?
- How is procurement spend trending over time?
- Which suppliers deliver the best reliability-to-risk profile?
- Which products contribute the most profit given list price vs. standard cost?

---

## Editing the reports

- Open the `.pbix` files in the latest version of [Power BI Desktop](https://powerbi.microsoft.com/desktop/).
- Keep the field / measure names aligned with the lakehouse tables in [`schema_and_tables.md`](../../../src/fabric/notebooks/schema/schema_and_tables.md) so refreshes continue to work after redeployment.
