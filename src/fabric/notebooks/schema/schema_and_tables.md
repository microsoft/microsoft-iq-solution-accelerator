# Schema and Tables Overview

This document provides a comprehensive overview of all database schemas and tables created by the notebooks in the schema folder.

## Summary Statistics

- **Total Notebooks**: 6
- **Total Schemas**: 6
- **Total Tables**: 23

---

## Detailed Table Inventory

| Notebook File | Schema Name | Table Name | Description |
|---------------|-------------|------------|-------------|
| model_customer.ipynb | customer | Customer | Core customer information and demographics |
| model_customer.ipynb | customer | CustomerTradeName | Business trade names for customers |
| model_customer.ipynb | customer | CustomerRelationshipType | Customer relationship classifications |
| model_customer.ipynb | customer | Location | Geographic location data |
| model_customer.ipynb | customer | CustomerAccount | Customer account management |
| model_product.ipynb | product | ProductLine | Product line definitions (Camping, Kitchen, Ski) |
| model_product.ipynb | product | Product | Product catalog and specifications |
| model_product.ipynb | product | ProductCategory | Product categorization by product line |
| model_sales.ipynb | sales | Order | Sales order headers |
| model_sales.ipynb | sales | OrderLine | Sales order line items |
| model_sales.ipynb | sales | OrderPayment | Payment transaction details |
| model_finance.ipynb | finance | invoice | Financial invoicing records |
| model_finance.ipynb | finance | account | Financial account management |
| model_finance.ipynb | finance | payment | Financial payment processing |
| model_inventory.ipynb | inventory | Warehouses | Warehouse locations and operational details |
| model_inventory.ipynb | inventory | Inventory | Current inventory levels and locations |
| model_inventory.ipynb | inventory | InventoryTransactions | Inventory movement audit trail |
| model_inventory.ipynb | inventory | PurchaseOrders | Purchase order headers |
| model_inventory.ipynb | inventory | PurchaseOrderItems | Purchase order line items |
| model_inventory.ipynb | inventory | DemandForecast | Predictive analytics and demand forecasting |
| model_supplychain.ipynb | supplychain | Suppliers | Supplier master data |
| model_supplychain.ipynb | supplychain | ProductSuppliers | Product-supplier relationship mapping |
| model_supplychain.ipynb | supplychain | SupplyChainEvents | Disruption events and impacts |

---

## Schema Distribution

| Schema Name | Number of Tables | Notebooks |
|-------------|-------------------|-----------|
| customer | 5 | model_customer.ipynb |
| product | 3 | model_product.ipynb |
| sales | 3 | model_sales.ipynb |
| finance | 3 | model_finance.ipynb |
| inventory | 6 | model_inventory.ipynb |
| supplychain | 3 | model_supplychain.ipynb |

---

## Business Domain Coverage

### Core Business Operations
- **Customer Management**: 5 tables for customer data, relationships, and accounts
- **Product Catalog**: 3 tables for product lines, products, and categories
- **Sales Processing**: 3 tables for orders, line items, and payments
- **Financial Operations**: 3 tables for invoicing, accounts, and payments

### Supply Chain Management
- **Inventory Control**: 6 tables for warehouses, stock levels, transactions, and forecasting
- **Supplier Management**: 3 tables for suppliers, product relationships, and disruption events

#### Inventory Schema Details
- **Warehouse Management**: 1 table for locations and operational details
- **Stock Control**: 2 tables for current levels and transaction audit trails
- **Purchase Orders**: 2 tables for procurement headers and line items
- **Demand Planning**: 1 table for predictive analytics and forecasting

#### Supply Chain Schema Details
- **Supplier Relationships**: 2 tables for supplier master data and product mappings
- **Risk Management**: 1 table for disruptions, events, and impact tracking

