# Data Source Descriptions - Fabric Lakehouse

## Overview

This document provides comprehensive descriptions of all data sources available in the Fabric lakehouse. All data is loaded as Delta tables and is analytics-ready for business intelligence and reporting purposes.

Data is synthetic and generated for demonstration purposes, covering realistic business transactions across three product categories: Camping, Kitchen, and Ski.

---

## Domain Structure

### Customer Domain (`customer` schema)

Master data entities for customer identity, accounts, locations, and relationship tiers.

---

#### Customer (`customer.Customer`)
**Purpose**: Core customer master data with demographics, contact information, and relationship management  
**Source**: Customer management systems and CRM platforms  
**Update Frequency**: Daily batch processing

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| CustomerId | STRING | Primary key, unique customer identifier | UUID format |
| CustomerTypeId | STRING | Classification of customer organization type | Individual, Business, Government |
| CustomerRelationshipTypeId | STRING | Customer tier/relationship level | Standard, Premium, VIP, SMB, Premier, Partner, Federal, State, Local |
| DateOfBirth | DATE | Customer's birth date | 1975-06-15, 1990-11-02 |
| CustomerEstablishedDate | DATE | Date the business relationship was established | 2018-03-01 |
| IsActive | BOOLEAN | Current status of customer account | true, false |
| FirstName | STRING | Customer's first name | Jane, Carlos |
| LastName | STRING | Customer's last name | Smith, Rivera |
| Gender | STRING | Customer gender | Male, Female |
| PrimaryPhone | STRING | Primary contact phone number | (512) 555-0123 |
| SecondaryPhone | STRING | Alternative contact phone number | (737) 555-0198 |
| PrimaryEmail | STRING | Primary email address | jane.smith@contoso.com |
| SecondaryEmail | STRING | Alternative email address | backup@contoso.com |
| CreatedBy | STRING | System/user who created the record | SampleGen, Sales |

**Business Rules**:
- Each customer has a unique `CustomerId`
- `CustomerRelationshipTypeId` determines pricing tiers and service levels
- `IsActive = true` is required for a customer to be eligible for new transactions
- Individual customers: Standard, Premium, VIP tiers
- Business customers: SMB, Premier, Partner tiers
- Government customers: Federal, State, Local tiers

---

#### CustomerRelationshipType (`customer.CustomerRelationshipType`)
**Purpose**: Lookup table defining customer relationship tier classifications  
**Update Frequency**: Infrequent (only when new tiers are introduced)

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| CustomerRelationshipTypeId | STRING | Primary key, unique tier identifier | UUID format |
| CustomerRelationshipTypeName | STRING | Human-readable tier name | Standard, Premium, VIP, SMB |
| CustomerRelationshipTypeDescription | STRING | Description of the tier and its benefits | "Top-tier individual customers with full service access" |

---

#### CustomerTradeName (`customer.CustomerTradeName`)
**Purpose**: Tracks business trade names used by customers, including historical names  
**Update Frequency**: As-needed during customer record updates

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| CustomerId | STRING | Foreign key to Customer table | UUID format |
| CustomerTypeId | STRING | Customer type context | Business, Government |
| TradeNameId | STRING | Unique trade name identifier | UUID format |
| TradeName | STRING | Trade name or DBA (Doing Business As) name | "Contoso Outdoors LLC" |
| PeriodStartDate | DATE | Start of period this trade name was active | 2020-01-01 |
| PeriodEndDate | DATE | End of period (NULL if currently active) | NULL, 2023-12-31 |
| CustomerTradeNameNote | STRING | Additional context about the trade name | "Rebranded from previous entity" |

---

#### Location (`customer.Location`)
**Purpose**: Geographic location data associated with customers, including billing and shipping addresses  
**Update Frequency**: Monthly batch processing  

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| LocationId | STRING | Primary key, unique location identifier | UUID format |
| CustomerId | STRING | Foreign key to Customer table | UUID format |
| LocationName | STRING | Descriptive name for the location | "HQ", "West Distribution" |
| IsActive | BOOLEAN | Whether the location is currently active | true, false |
| AddressLine1 | STRING | Street address | "1000 Main St" |
| AddressLine2 | STRING | Secondary address info | "Apt 5", "Suite 200" |
| City | STRING | City name | Austin, Seattle |
| StateId | STRING | State abbreviation | TX, WA, NY |
| ZipCode | STRING | ZIP/Postal code | 78701, 98101 |
| CountryId | STRING | Country code | US, CA |
| SubdivisionName | STRING | State or province full name | Texas, Washington |
| Region | STRING | Business region classification | Northeast, West Coast, Midwest, South |
| Latitude | DECIMAL(10,7) | Geographic latitude | 30.2672000 |
| Longitude | DECIMAL(10,7) | Geographic longitude | -97.7431000 |
| Note | STRING | Additional location notes | "Primary shipping address" |

---

#### CustomerAccount (`customer.CustomerAccount`)
**Purpose**: Financial account groupings that link customers to their purchasing accounts  
**Update Frequency**: Real-time during account creation/modification

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| CustomerAccountId | STRING | Primary key, unique account identifier | UUID format |
| ParentAccountId | STRING | Parent account for hierarchical groupings | UUID format, NULL |
| CustomerAccountName | STRING | Business-readable account name | "Contoso Northwest Account" |
| CustomerId | STRING | Foreign key to Customer table | UUID format |
| IsoCurrencyCode | STRING | Currency used for this account | USD, EUR, GBP |

---

### Product Domain (`product` schema)

Product catalog and category data used across sales, inventory, and supply chain domains.

---

#### Product (`product.Product`)
**Purpose**: Product catalog with pricing, specifications, and categorization  
**Update Frequency**: Weekly batch processing  

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| ProductID | STRING | Primary key, unique product identifier | UUID format |
| ProductName | STRING | Full product name with specification | "Summit Pro Tent 4-Person" |
| ProductDescription | STRING | Detailed product description | "Lightweight 4-season tent..." |
| BrandName | STRING | Product brand | Contoso, Fabrikam |
| ProductNumber | STRING | Internal product SKU/number | SKU-CAMP-001 |
| Color | STRING | Color variant | Black, Red, Blue, Multi |
| ProductModel | STRING | Model or series name | "Summit Pro", "Trail Lite" |
| ProductCategoryID | STRING | Foreign key to ProductCategory | UUID format |
| CategoryName | STRING | Denormalized category name | Camping, Kitchen, Ski |
| ListPrice | DECIMAL(18,2) | Suggested retail price | 249.99, 1499.00 |
| StandardCost | DECIMAL(18,2) | Manufacturing or procurement cost | 124.50, 750.00 |
| Weight | DECIMAL(18,3) | Product weight | 2.500, 15.750 |
| WeightUom | STRING | Unit of measure for weight | kg, lb, oz |
| ProductStatus | STRING | Current lifecycle status | active, inactive, discontinued |
| CreatedDate | DATE | Date product was created in system | 2023-01-15 |
| SellStartDate | DATE | Date product became available for sale | 2023-02-01 |
| SellEndDate | DATE | Date product was discontinued (NULL if active) | NULL, 2025-12-31 |
| IsoCurrencyCode | STRING | Currency for pricing | USD |
| UpdatedDate | DATE | Last update date | 2025-06-01 |
| CreatedBy | STRING | User/system who created the record | SampleGen |
| UpdatedBy | STRING | User/system who last updated the record | SampleGen |

**Business Rules**:
- `ListPrice` must be greater than `StandardCost`
- `ProductStatus = 'active'` is required for a product to be sold
- `SellEndDate = NULL` means the product is currently available

---

#### ProductCategory (`product.ProductCategory`)
**Purpose**: Hierarchical product categorization used for reporting and supply chain  
**Update Frequency**: Quarterly during catalog reviews

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| CategoryID | STRING | Primary key, unique category identifier | UUID format |
| ParentCategoryId | STRING | Parent category for hierarchy (NULL = top level) | UUID format, NULL |
| CategoryName | STRING | Category display name | Camping, Kitchen, Ski |
| CategoryDescription | STRING | Description of the category | "Outdoor camping equipment and accessories" |
| BrandName | STRING | Brand associated with this category | Contoso |
| BrandLogoUrl | STRING | URL to brand logo image | https://... |
| IsActive | BOOLEAN | Whether this category is currently active | true, false |

---

### Sales Domain (`sales` schema)

Sales transaction data covering orders, line items, and payment records.

---

#### Order (`sales.Order`)
**Purpose**: Sales order headers with customer, pricing, and status information  
**Update Frequency**: Real-time during order processing

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| OrderId | STRING | Primary key, unique order identifier | UUID format |
| SalesChannelId | STRING | Sales channel identifier | Fabric |
| OrderNumber | STRING | Business-readable order number | F100000, F100001 |
| CustomerId | STRING | Foreign key to Customer table | UUID format |
| CustomerAccountId | STRING | Foreign key to CustomerAccount table | UUID format |
| OrderDate | DATE | Date order was placed | 2025-03-15 |
| OrderStatus | STRING | Current order processing status | Completed, Pending, Cancelled |
| SubTotal | DECIMAL(18,2) | Order total before tax | 2399.95 |
| TaxAmount | DECIMAL(18,2) | Tax amount (5% flat rate) | 120.00 |
| OrderTotal | DECIMAL(18,2) | Final total including tax | 2519.95 |
| PaymentMethod | STRING | Payment method used | VISA, MC, PayPal, Discover |
| IsoCurrencyCode | STRING | Currency code | USD |
| CreatedBy | STRING | System/user who created the order | SampleGen |

**Business Rules**:
- `OrderTotal = SubTotal + TaxAmount`
- Tax rate is 5% flat across all orders
- `OrderStatus = 'Completed'` indicates successful fulfillment and payment
- `PaymentMethod` abbreviations: MC (MasterCard), VISA, PayPal, Discover

---

#### OrderLine (`sales.OrderLine`)
**Purpose**: Individual line items within sales orders, linking products to orders

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| OrderId | STRING | Foreign key to Order table | UUID format |
| OrderLineNumber | INT | Sequential line number within the order | 1, 2, 3 |
| ProductId | STRING | Foreign key to Product table | UUID format |
| ProductName | STRING | Denormalized product name | "Summit Pro Tent 4-Person" |
| Quantity | DECIMAL(18,2) | Number of units ordered | 1, 2, 5 |
| UnitPrice | DECIMAL(18,2) | Price per unit at time of order | 249.99 |
| LineTotal | DECIMAL(18,2) | Quantity × UnitPrice | 499.98 |
| DiscountAmount | DECIMAL(18,2) | Discount applied to the line | 0.00, 25.00 |
| TaxAmount | DECIMAL(18,2) | Tax for this line item (5%) | 25.00 |

---

#### OrderPayment (`sales.OrderPayment`)
**Purpose**: Payment transaction records linked to orders  

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| OrderId | STRING | Foreign key to Order table | UUID format |
| PaymentMethod | STRING | Payment method used | VISA, MC, Discover, PayPal |
| TransactionId | STRING | Unique payment transaction identifier | UUID format |

---

### Finance Domain (`finance` schema)

Financial data covering accounts, invoicing, and payment processing.

---

#### invoice (`finance.invoice`)
**Purpose**: Invoice records for billing customers, linked to sales orders

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| InvoiceId | STRING | Primary key, unique invoice identifier | UUID format |
| InvoiceNumber | STRING | Business-readable invoice number | INV-F-100000 |
| CustomerId | STRING | Foreign key to Customer table | UUID format |
| OrderId | STRING | Foreign key to Sales Order table | UUID format |
| InvoiceDate | DATE | Date invoice was created | 2025-03-15 |
| DueDate | DATE | Payment due date | 2025-04-14 |
| SubTotal | DECIMAL(18,2) | Invoice amount before tax | 2399.95 |
| TaxAmount | DECIMAL(18,2) | Tax portion of invoice | 120.00 |
| TotalAmount | DECIMAL(18,2) | Total invoice amount | 2519.95 |
| InvoiceStatus | STRING | Current invoice status | Paid, Pending, Overdue, Cancelled |
| CreatedBy | STRING | System/user who created the invoice | SampleGen |

---

#### account (`finance.account`)
**Purpose**: Financial accounts tracking receivables and payables per customer

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| AccountId | STRING | Primary key, unique account identifier | UUID format |
| AccountNumber | STRING | Business-readable account number | ACC-Fabric-1000 |
| CustomerId | STRING | Foreign key to Customer table | UUID format |
| AccountType | STRING | Type of financial account | Receivable, Payable, Credit, Cash |
| AccountStatus | STRING | Current account status | Active, Closed, Suspended |
| CreatedDate | DATE | Account creation date | 2022-12-21 |
| ClosedDate | DATE | Closure date (NULL if still open) | NULL, 2025-06-30 |
| Balance | DECIMAL(18,2) | Current account balance | 0.00, 20642.95, -1500.00 |
| Currency | STRING | Account currency | USD, EUR, GBP |
| Description | STRING | Account purpose description | "Customer receivable account (Fabric)" |
| CreatedBy | STRING | User/system who created the account | SampleGen |

**Business Rules**:
- `AccountType = 'Receivable'` → money owed to the company
- `AccountType = 'Payable'` → money the company owes
- `AccountStatus = 'Suspended'` → account frozen, no new transactions
- `ClosedDate = NULL` for all currently open accounts

---

#### payment (`finance.payment`)
**Purpose**: Payment transaction records for money received from customers

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| PaymentId | STRING | Primary key, unique payment identifier | UUID format |
| InvoiceId | STRING | Foreign key to Invoice table | UUID format |
| CustomerId | STRING | Foreign key to Customer table | UUID format |
| PaymentDate | DATE | Date payment was received | 2025-03-20 |
| PaymentAmount | DECIMAL(18,2) | Amount paid | 2519.95 |
| PaymentMethod | STRING | Payment method used | VISA, MC, Discover, PayPal |
| PaymentStatus | STRING | Current payment status | Completed, Pending, Failed, Refunded |
| CreatedBy | STRING | User/system who created the record | SampleGen |

---

### Inventory Domain (`inventory` schema)

Inventory management data covering warehouses, stock levels, purchase orders, and demand forecasting.

---

#### Warehouses (`inventory.Warehouses`)
**Purpose**: Master data for warehouse locations and operational details

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| WarehouseID | STRING | Primary key | Main, Backup, Regional |
| WarehouseName | STRING | Full warehouse name | "Main Distribution Center" |
| DisplayName | STRING | Short display name for reports | "Main DC" |
| Type | STRING | Warehouse type | Main, Backup, Regional |
| Status | STRING | Operational status | Active, Inactive, Maintenance |
| AddressCity | STRING | City | Dallas, Chicago, Seattle |
| AddressState | STRING | State abbreviation | TX, IL, WA |
| ManagerName | STRING | Warehouse manager | "John Martinez" |
| Priority | DECIMAL(3,2) | Inventory allocation priority (0.0–1.0) | 0.60, 0.25, 0.15 |
| MaxCapacity | INT | Maximum storage capacity (units) | 50000 |
| AutomationLevel | STRING | Level of warehouse automation | High, Medium, Low |

---

#### Inventory (`inventory.Inventory`)
**Purpose**: Current stock levels per product per warehouse

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| InventoryID | INT | Primary key | 1, 2, 3 |
| ProductID | INT | Foreign key to Product table | 101, 202 |
| ProductName | STRING | Denormalized product name | "Summit Pro Tent 4-Person" |
| ProductCategory | STRING | Product category | Camping, Kitchen, Ski |
| WarehouseLocation | STRING | Foreign key to Warehouses | Main, Backup, Regional |
| CurrentStock | INT | Available quantity in warehouse | 500, 23, 0 |
| ReservedStock | INT | Stock allocated but not yet shipped | 50 |
| AvailableStock | INT | CurrentStock − ReservedStock | 450 |
| SafetyStockLevel | INT | Minimum acceptable stock threshold | 100 |
| ReorderPoint | INT | Trigger point for new purchase orders | 150 |
| MaxStockLevel | INT | Maximum stock allowed in warehouse | 2000 |
| AverageCost | DECIMAL(10,2) | Weighted average unit cost | 124.50 |
| Status | STRING | Stock status classification | Active, Excess, Low Stock, Out of Stock |

---

#### InventoryTransactions (`inventory.InventoryTransactions`)
**Purpose**: Full audit trail of all inventory movements

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| TransactionID | INT | Primary key | 1, 2, 3 |
| ProductName | STRING | Denormalized product name | "Trail Lite Sleeping Bag" |
| ProductCategory | STRING | Product category | Camping, Kitchen, Ski |
| WarehouseLocation | STRING | Warehouse where movement occurred | Main, Backup |
| TransactionType | STRING | Type of movement | Receipt, Sale, Adjustment, Transfer |
| TransactionDate | TIMESTAMP | When the transaction occurred | 2025-11-01 09:00:00 |
| Quantity | INT | Units moved (positive = in, negative = out) | 200, -15 |
| UnitCost | DECIMAL(10,2) | Cost per unit at time of transaction | 124.50 |
| TotalValue | DECIMAL(10,2) | Total monetary value of transaction | 24900.00 |
| ReferenceNumber | STRING | PO number, order number, etc. | PO-001, F100055 |
| ReasonCode | STRING | Reason for adjustment or transfer | Cycle Count, Damage, Return |
| StockBefore | INT | Stock level before transaction | 300 |
| StockAfter | INT | Stock level after transaction | 500 |

---

#### PurchaseOrders (`inventory.PurchaseOrders`)
**Purpose**: Purchase order headers for product procurement

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| PurchaseOrderID | INT | Primary key | 1, 2, 3 |
| PurchaseOrderNumber | STRING | Business-readable PO identifier | PO-2025-001 |
| SupplierID | INT | Foreign key to Suppliers table | 1, 2, 3 |
| SupplierName | STRING | Denormalized supplier name | "Contoso Camping Equipment" |
| OrderDate | DATE | Date PO was placed | 2025-10-15 |
| ExpectedDeliveryDate | DATE | Expected delivery date | 2025-11-01 |
| ActualDeliveryDate | DATE | Actual delivery date (NULL if pending) | NULL, 2025-11-03 |
| Status | STRING | PO processing status | Pending, Shipped, Delivered, Cancelled |
| TotalOrderValue | DECIMAL(12,2) | Total monetary value of PO | 48750.00 |
| DeliveryLocation | STRING | Warehouse receiving the order | Main, Backup, Regional |
| Priority | STRING | Order urgency | Low, Medium, High, Urgent |

**Business Rules**:
- `ActualDeliveryDate = NULL` indicates the order is still in transit or pending
- `Status = 'Delivered'` is set once goods are physically received

---

#### PurchaseOrderItems (`inventory.PurchaseOrderItems`)
**Purpose**: Line items within purchase orders

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| PurchaseOrderItemID | INT | Primary key | 1, 2, 3 |
| PurchaseOrderID | INT | Foreign key to PurchaseOrders | 1, 2 |
| PurchaseOrderNumber | STRING | Denormalized PO number | PO-2025-001 |
| ProductName | STRING | Denormalized product name | "Summit Pro Tent 4-Person" |
| ProductCategory | STRING | Product category | Camping, Kitchen, Ski |
| QuantityOrdered | INT | Units requested | 200 |
| QuantityReceived | INT | Units actually received | 200, 150 |
| UnitCost | DECIMAL(10,2) | Per-unit wholesale cost | 124.50 |
| LineTotal | DECIMAL(12,2) | QuantityOrdered × UnitCost | 24900.00 |
| Status | STRING | Line item fulfillment status | Pending, Partial, Complete, Cancelled |
| ExpectedDate | DATE | Expected receipt date for this line | 2025-11-01 |
| ReceivedDate | DATE | Actual receipt date (NULL if pending) | NULL, 2025-11-03 |

---

#### DemandForecast (`inventory.DemandForecast`)
**Purpose**: Pre-generated demand forecasts for inventory planning

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| ForecastID | INT | Primary key | 1, 2, 3 |
| ProductName | STRING | Denormalized product name | "Trail Lite Sleeping Bag" |
| ProductCategory | STRING | Product category | Camping, Kitchen, Ski |
| ForecastDate | DATE | Future date being forecasted | 2026-04-01 |
| ForecastPeriod | STRING | Forecast granularity | Weekly, Monthly, Quarterly |
| PredictedDemand | INT | Forecasted units needed | 150 |
| ConfidenceLevel | DECIMAL(5,2) | Confidence score (0–100%) | 85.50 |
| SeasonalMultiplier | DECIMAL(5,2) | Seasonal adjustment factor | 1.25, 0.80 |
| TrendDirection | STRING | Directional trend | Growing, Stable, Declining |
| BaselineDemand | INT | Historical average demand | 120 |
| MethodUsed | STRING | Forecasting algorithm or method | "Moving Average", "Seasonal Decomposition" |

**Business Rules**:
- Demand forecasts are synthetically generated and are for planning illustration only
- `ConfidenceLevel` represents model confidence, not actual predictive accuracy

---

### Supply Chain Domain (`supplychain` schema)

Supplier master data, product-supplier relationships, and disruption event tracking.

---

#### Suppliers (`supplychain.Suppliers`)
**Purpose**: Master data for product suppliers and backup supplier network

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| SupplierID | INT | Primary key | 1, 2, 3, 4, 5 |
| SupplierName | STRING | Full supplier name | "Contoso Camping Equipment" |
| SupplierType | STRING | Supplier role in network | Primary, Secondary |
| Status | STRING | Current supplier operational status | Active, Disrupted, Inactive |
| ProductCategory | STRING | Category this supplier covers | Camping, Kitchen, Ski, Multi |
| PrimarySupplierID | INT | Primary supplier this backs up (NULL if primary) | NULL, 1 |
| LeadTimeDays | INT | Standard delivery lead time in days | 7, 14, 21 |
| ReliabilityScore | INT | Supplier performance score (0–100) | 92, 78 |
| Location | STRING | Supplier location | "Dallas, TX", "Chicago, IL" |
| ContactEmail | STRING | Primary supplier contact email | supplier@contoso.com |

**Supplier Network**:
- Camping: Contoso Ltd (Primary), Worldwide Importers (Secondary)
- Kitchen: Proseware Inc (Primary), Worldwide Importers (Secondary)
- Ski: Alpine Ski House (Primary), Worldwide Importers + Fabrikam (Secondary)

---

#### ProductSuppliers (`supplychain.ProductSuppliers`)
**Purpose**: Maps products to their suppliers with pricing and ordering terms

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| ProductSupplierID | INT | Primary key | 1, 2, 3 |
| ProductID | INT | Foreign key to Product table | 101 |
| ProductName | STRING | Denormalized product name | "Summit Pro Tent 4-Person" |
| ProductCategory | STRING | Product category | Camping, Kitchen, Ski |
| SupplierID | INT | Foreign key to Suppliers table | 1 |
| SupplierName | STRING | Denormalized supplier name | "Contoso Camping Equipment" |
| SupplierProductCode | STRING | Supplier's internal SKU | CCA-TENT-001 |
| WholesaleCost | DECIMAL(10,2) | Supplier cost per unit (60–80% of retail) | 124.50 |
| MinOrderQuantity | INT | Minimum order size | 50 |
| MaxOrderQuantity | INT | Maximum order size (NULL = no limit) | 500, NULL |
| LeadTimeDays | INT | Product-specific lead time | 14 |
| Status | STRING | Relationship status | Active, Discontinued |

---

#### SupplyChainEvents (`supplychain.SupplyChainEvents`)
**Purpose**: Consolidated disruption events and their business impact assessment

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| EventID | INT | Primary key | 1, 2, 3 |
| DisruptionType | STRING | Category of disruption | Weather, Political, Economic, Pandemic, Transport, Supplier |
| EventName | STRING | Short descriptive event name | "Pacific Coast Storm System" |
| Severity | STRING | Disruption severity | Low, Medium, High, Critical |
| Status | STRING | Current event status | Active, Monitoring, Resolved |
| StartDate | DATE | When disruption began | 2025-11-15 |
| EndDate | DATE | When resolved (NULL if ongoing) | NULL, 2026-01-10 |
| GeographicArea | STRING | Affected region | "Pacific Northwest", "Global" |
| AlertLevel | STRING | Visual alert level | Green, Yellow, Orange, Red |
| SupplierID | INT | Specific supplier affected (NULL if general) | NULL, 2 |
| ProductCategory | STRING | Affected product category | Camping, Kitchen, Ski, NULL |
| ImpactLevel | STRING | Impact severity on operations | None, Low, Medium, High |
| DeliveryDelay | INT | Additional days of delay caused | 0, 5, 14 |
| CostIncrease | DECIMAL(5,2) | Percentage cost increase (0–100) | 0.00, 12.50 |
| AlternativeAction | STRING | Mitigation action taken | "Switched to backup supplier" |
| EstimatedRevenueImpact | DECIMAL(12,2) | Estimated financial impact | 50000.00 |

**Business Rules**:
- `EndDate = NULL` means the disruption is still ongoing
- `SupplierID = NULL` means the event is a general/market-wide disruption
- `AlertLevel` escalates: Green → Yellow → Orange → Red

---

## Data Quality and Governance

### Data Quality Standards
- **Completeness**: All required fields are populated; nullable fields are clearly documented above
- **Accuracy**: Data validated against business rules during generation
- **Consistency**: Standardized formats and reference values across all domains
- **Referential Integrity**: All foreign key relationships are consistent across tables

### Key Relationships

**Within-Domain Relationships**

*Customer Domain:*
- `customer.Customer` ↔ `customer.CustomerRelationshipType`: Many-to-one via `CustomerRelationshipTypeId`
- `customer.Customer` ↔ `customer.CustomerTradeName`: One-to-many via `CustomerId`
- `customer.Customer` ↔ `customer.Location`: One-to-many via `CustomerId`
- `customer.Customer` ↔ `customer.CustomerAccount`: One-to-many via `CustomerId`
- `customer.CustomerAccount` ↔ `customer.CustomerAccount` (parent): Self-referential hierarchy via `ParentAccountId`

*Product Domain:*
- `product.Product` ↔ `product.ProductCategory`: Many-to-one via `ProductCategoryID`
- `product.ProductCategory` ↔ `product.ProductCategory` (parent): Self-referential hierarchy via `ParentCategoryId`

*Sales Domain:*
- `sales.Order` ↔ `sales.OrderLine`: One-to-many via `OrderId`
- `sales.Order` ↔ `sales.OrderPayment`: One-to-one via `OrderId`

*Finance Domain:*
- `finance.invoice` ↔ `finance.payment`: One-to-one via `InvoiceId`

*Inventory Domain:*
- `inventory.PurchaseOrders` ↔ `inventory.PurchaseOrderItems`: One-to-many via `PurchaseOrderID`

*Supply Chain Domain:*
- `supplychain.Suppliers` ↔ `supplychain.ProductSuppliers`: One-to-many via `SupplierID`
- `supplychain.Suppliers` ↔ `supplychain.SupplyChainEvents`: One-to-many via `SupplierID`
- `supplychain.Suppliers` ↔ `supplychain.Suppliers` (primary): Self-referential via `PrimarySupplierID` (secondary suppliers reference their primary)

**Cross-Domain Relationships**

*Customer → Sales:*
- `customer.Customer` ↔ `sales.Order`: One-to-many via `CustomerId`
- `customer.CustomerAccount` ↔ `sales.Order`: One-to-many via `CustomerAccountId`

*Customer → Finance:*
- `customer.Customer` ↔ `finance.invoice`: One-to-many via `CustomerId`
- `customer.Customer` ↔ `finance.account`: One-to-many via `CustomerId`
- `customer.Customer` ↔ `finance.payment`: One-to-many via `CustomerId`

*Product → Sales:*
- `product.Product` ↔ `sales.OrderLine`: One-to-many via `ProductId`

*Product → Inventory:*
- `product.Product` ↔ `inventory.Inventory`: One-to-many via `ProductID`
- `product.Product` ↔ `inventory.InventoryTransactions`: One-to-many via `ProductID`
- `product.Product` ↔ `inventory.PurchaseOrderItems`: One-to-many via `ProductID`
- `product.Product` ↔ `inventory.DemandForecast`: One-to-many via `ProductID`

*Product → Supply Chain:*
- `product.Product` ↔ `supplychain.ProductSuppliers`: One-to-many via `ProductID`

*Sales → Finance:*
- `sales.Order` ↔ `finance.invoice`: One-to-one via `OrderId`

*Inventory Warehouse Links:*
- `inventory.Warehouses` ↔ `inventory.Inventory`: One-to-many via `WarehouseLocation` / `WarehouseID`
- `inventory.Warehouses` ↔ `inventory.InventoryTransactions`: One-to-many via `WarehouseLocation` / `WarehouseID`
- `inventory.Warehouses` ↔ `inventory.PurchaseOrders`: One-to-many via `DeliveryLocation` / `WarehouseID`

*Supply Chain → Inventory:*
- `supplychain.Suppliers` ↔ `inventory.PurchaseOrders`: One-to-many via `SupplierID`

### Synthetic Data Notice
All data in this environment is synthetically generated for demonstration and learning purposes. Data patterns, relationships, and business rules reflect realistic scenarios but do not represent actual customer, product, or financial information.
