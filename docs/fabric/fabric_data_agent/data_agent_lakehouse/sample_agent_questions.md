# Sample Agent Test Questions — Fabric IQ Data Agent

## Overview

This document contains a collection of test questions designed to validate the Fabric Data Agent's capabilities across different scenarios and complexity levels. Questions cover data exploration, business analytics, cross-domain analysis, and supply chain intelligence across the six domain schemas: `customer`, `product`, `sales`, `finance`, `inventory`, and `supplychain`.

---

## Sample Questions Table

| # | Level | Domain | Question | Notes | Test Result F2 | Test Results F8 |
|---|-------|--------|----------|-------|----------------|-----------------|
| 1 | Simple | Product | How many products do we have? | Single-entity count | Good | Good |
| 2 | Simple | Product | List all product categories. | Entity listing + display names | Good | Good |
| 3 | Simple | Inventory | List all warehouses. | Entity listing | Good | Good |
| 4 | Simple | Supply Chain | List all suppliers. | Entity listing | Good | Good |
| 5 | Intermediate | Customer | Show me the breakdown of customers by customer type (Individual, Business, Government). | Customer type segmentation | **no answer** | Good |
| 6 | Intermediate | Customer | How many customers are associated with each geographic region? | Geographic distribution | Good | Good |
| 7 | Intermediate | Sales | How many line items are typically included in a single order? | Order complexity analysis | Good | Good |
| 8 | Intermediate | Finance | What is the total amount of payments received, broken down by payment method? | Payment receipts summary | Good | Good |
| 9 | Intermediate | Inventory | Which products are currently out of stock or below their reorder point across all warehouses? | Stock alert view across all warehouses | Good | Good |
| 10 | Intermediate | Inventory | What is the current stock of Alpine Explorer Tent? | Product → Inventory join | Good | Good |
| 11 | Intermediate | Inventory | What is the total inventory value across all warehouses? | Inventory valuation | Good | Good |
| 12 | Intermediate | Inventory | Which warehouse has the most available stock? | Aggregation + sorting | Good | Good |
| 13 | Intermediate | Inventory | How many of Coffee Mug is reserved in stock? | Specific product lookup | Good | Good |
| 14 | Intermediate | Supply Chain | Which products are supplied by Fabrikam? | Bridge entity traversal. Supplier names: Fabrikam, Contoso Ltd, Proseware Inc, Alpine Ski House, Worldwide Importers | Good           | Good |
| 15 | Intermediate | Supply Chain | Are there any active or monitored supply chain disruptions? What is the severity and estimated impact? | Disruption risk view | Good | Good |
| 16 | Intermediate | Supply Chain | Which products have multiple suppliers available? | Supplier redundancy check | Good | Good |
| 17 | Intermediate | Supply Chain | Which suppliers have the shortest lead times, and how does that compare to our current inventory levels? | Lead time vs stock analysis | Good | Good |
| 18 | Advanced | Supply Chain | Which suppliers were affected by weather disruptions? | Event impact traversal | Good | Good |
| 19 | Advanced | Inventory | What is total forecasted demand for Summit Breeze Jacket? | Product-specific forecast lookup | Good | Good |
| 20 | Advanced | Inventory | List top 5 products by current stock in Main Distribution Center. | Multi-hop join + sort + limit | Good           | Good |
| 21 | Advanced | Business Analytics | Which product categories generate the most revenue and have the highest profit margins? | Category performance comparison | **no answer** | Good |
| 22 | Advanced | Business Analytics | Show me the top 5 products by total revenue, including units sold and gross margin. | Top product analysis | Good | Good |
| 23 | Advanced | Business Analytics | Which products are at risk of running out based on current stock levels and recent sales velocity? | Inventory risk analysis | Good | Good |
