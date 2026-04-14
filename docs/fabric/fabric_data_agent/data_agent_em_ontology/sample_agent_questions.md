# Sample Agent Test Questions

## Overview

This document provides sample questions to test the Data Agent Entity Model's capabilities across product inventory, warehouse operations, supply chain management, and demand forecasting scenarios.

## How to Use These Questions

The questions below contain placeholders in square brackets (e.g., `[Product Name]`) that you should replace with actual values from your system. You can also ask the data agent to show you available options first.

### Example Values

**Product Names:**

- Adventurer Pro Backpack
- Alpine Explorer Tent  
- Espresso Machine
- Food Storage Set
- Waterproof Ski Pants
- Ski Boot Bag - Premium

**Product Categories:**
- Backpacks
- Camping Stoves
- Ice Cream Dishes
- Cooking Utensils
- Ski Apparel
- Winter Footwear

**Warehouse Names:**
- Main Warehouse
- Regional Warehouse
- Backup Warehouse

**Supplier Names:**
- Ask the data agent: "List all suppliers" to get available supplier names

> **Tip:** You can ask the data agent to "show me all product categories" or "list all product names" to discover available values for testing. 
---

## Test Questions

| # | Domain | Question | Notes |
|---|--------|----------|----------|
| 1 | Supply Chain | List all suppliers. | Get available supplier names |
| 2 | Inventory | List all warehouses. | Get available warehouse names |
| 3 | Product | List all product categories. | Get available category names |
| 4 | Product | Show all products in the category tents / Show all products in the category [**Category Name**]. <br /><br />(Example Categories: Tents, Backpacks, Camping Tables, Coffee Makers, Bakeware, Ski Boots, Winter Footwear) | Category product listing |
| 5 | Inventory | List products that are below their reorder point. | Low stock identification |
| 6 | Inventory | List all products stored in main warehouse, show product ID, Product Name, and Quantity on hand. | Warehouse inventory query |
| 7 | Inventory | What is the available stock for Coffee Maker in main warehouse? | Multi-warehouse stock query |
| 8 | Inventory | Show me products with inventory status LowStock and show results in tabular format. | Stock status filtering |
| 9 | Inventory | How much of Coffee Mugs is reserved in stock? <br /><br />(Example Product Names: BaseCamp Folding Table, TrailLite Daypack, Coffee Maker, Coffee Mug, Professional Ski Helmet, Winter Boots - Insulated) | Reserved stock inquiry |
| 10 | Inventory | Which warehouse has the most capacity? | Capacity analysis |
| 11 | Inventory(*) | Show all purchase orders made to supplier Fabrikam, with purchase order details such as PO, TotalOrderValue, and status. Show results in tabular format. <br /><br />Other examples: Contoso Ltd, Alpine Ski House, Fabrikam, Worldwide Importers, Proseware Inc | Supplier order history |
| 12 | Supply Chain (*) | Which products are supplied by Proseware? <br /><br />(Example Supplier Names: Contoso, Proseware, Alpine Ski House, Fabrikam, Worldwide Importers) | Supplier product catalog |
| 13 | Supply Chain (*) | List all supply chain events from entity named supplychainevents. | Product-specific disruptions |
| 14 | Inventory | What is the demand forecast (demandforecast) for Tents for May 2026? (Example Categories: Tents, Backpacks, Camping Tables, Coffee Makers, Bakeware, Ski Boots, Winter Footwear) | Category demand prediction |



## Appendix: Example Q&A

**Question** to fabric data agent:  "List all product categories"

**Agent Answer**: 

Here are all the product categories in the system:

Camping:

- Tents
- Backpacks
- Hiking Clothing
- Hiking Footwear
- Camping Tables
- Camping Stoves
- Sleeping Bags
- Lighting

Kitchen:

- Coffee Makers
- Cutlery
- Cups & Mugs
- Serving Dishes
- Ice Cream Dishes
- Mixing Bowls
- Bakeware
- Storage Containers
- Cooking Utensils
- Measuring Tools
- Small Appliances
- Cutting Boards

Ski:

- Alpine Skis
- Cross-Country Skis
- Ski Poles
- Ski Boots
- Snowboards & Equipment
- Ski Apparel
- Ski Accessories
- Safety Equipment
- Ski Maintenance
- Winter Footwear