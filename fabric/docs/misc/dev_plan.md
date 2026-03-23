

# Next steps

1. Create Dashboards Sales + Supply Chain Management 

2. Create Ontology - using both lakehouse and PBI semantic models as data source if possible

3. Create Data Agent using Ontology as the data source. 

   We may still need to add instructions to use GQL. 

   

## **Fabric Auto-Ontology Discovery**

✅ **Semantic Layer Auto-Generation** - Fabric analyzes your 21 tables and infers relationships
✅ **Foreign Key Detection** - Automatically maps `OrderId`, `ProductId`, `CustomerId` connections
✅ **Data Type Intelligence** - Understands dates, quantities, currencies, categories
✅ **Business Logic Inference** - Learns patterns from your 5.5 years of sales data

**You're 100% correct** - just point it at your lakehouse and let it work!

## **Dashboard Development Priority**

Since you have rich data + working ontology auto-discovery, let's focus on:

### 🎯 **Sales Dashboard (5+ Years)**

recreate the sales dashboard similar to current UDF dashboard. 

Keep all tiles (code underneath is needs some modification as the lakehosue schema and tables are restructured).

Sales data generated for 2021-01-01 to 2026-04-30. Replace gender distribution tile with revenue by product line (sales/order table)



### 📈 **Supply Chain Dashboard** Data Source 

Below is used as a base. 

![revenue_trend_graph_default_20210101_to_20260430](../src/datagen/output/supply_chain_data_default_20250101_to_20260430.png)

