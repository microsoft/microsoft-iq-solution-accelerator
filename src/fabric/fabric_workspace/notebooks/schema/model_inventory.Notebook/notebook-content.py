# Fabric notebook source


# MARKDOWN ********************

# # Supply Chain Data Model - Inventory & Purchase Orders
# 
# ## Schema Structure
# - **Warehouses Table**: Master data for warehouse locations, addresses, and operational details
# - **Inventory Table**: Current stock levels and warehouse locations
# - **InventoryTransactions Table**: All stock movements (receipts, sales, adjustments)
# - **PurchaseOrders Table**: Order headers with supplier and timing information
# - **PurchaseOrderItems Table**: Line items with product details and quantities
# - **DemandForecast Table**: Predictive analytics for future demand planning
# - Supports inventory tracking with purchase order integration, warehouse management, and demand forecasting

# CELL ********************

################################################################################################
# Schema Configuration - You can define different value here
################################################################################################

# Schema Configuration
SCHEMA_NAME = "inventory"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA_NAME}")
print(f"✅ {SCHEMA_NAME} schema ready!")

# CELL ********************

# Create all Inventory and Purchase Order tables
# 1. Warehouses - Master data for warehouse locations and details
# 2. Inventory - Current stock levels and warehouse locations
# 3. InventoryTransactions - All stock movements (receipts, sales, adjustments) 
# 4. PurchaseOrders - Order headers with supplier and timing information
# 5. PurchaseOrderItems - Line items with product details and quantities
# 6. DemandForecast - Predictive analytics for future demand planning

# CELL ********************

# 1. Create Warehouses table for master warehouse data
TABLE_NAME = "Warehouses"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    WarehouseID STRING,         -- Primary key: Main, Backup, Regional
    WarehouseName STRING,       -- Full warehouse name
    DisplayName STRING,         -- Display name for reports and charts
    Type STRING,                -- Main, Backup, Regional
    Status STRING,              -- Active, Inactive, Maintenance
    Location STRING,            -- City, State format for legacy compatibility
    
    -- Address Information
    AddressStreet STRING,       -- Street address
    AddressCity STRING,         -- City name
    AddressState STRING,        -- State abbreviation
    AddressZipCode STRING,      -- ZIP/Postal code
    AddressCountry STRING,      -- Country code
    
    -- Contact Information
    Phone STRING,               -- Main phone number
    Email STRING,               -- Operations email
    ManagerName STRING,         -- Warehouse manager name
    ManagerEmail STRING,        -- Manager direct email
    
    -- Operational Information
    Priority DECIMAL(3,2),      -- Inventory allocation priority (0.0-1.0)
    MaxCapacity INT,            -- Maximum storage capacity
    OperatingHours STRING,      -- Operating schedule
    StaffCount INT,            -- Number of employees
    AutomationLevel STRING,     -- High, Medium, Low
    DeliveryName STRING,        -- Name used for purchase order delivery
    
    -- System Fields
    CreatedBy STRING,           -- System user
    CreatedDate DATE,      -- Record creation date
    LastUpdated DATE       -- Last modification date
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

# CELL ********************

# 2. Create Inventory table for current stock levels
TABLE_NAME = "Inventory"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    InventoryID STRING,
    ProductID STRING,           -- Links to existing Product table
    ProductName STRING,         -- Denormalized for usability
    ProductCategory STRING,     -- Camping, Kitchen, Ski
    WarehouseLocation STRING,   -- Foreign key to Warehouses.WarehouseID
    CurrentStock INT,           -- Current available quantity
    ReservedStock INT,          -- Stock allocated but not shipped
    AvailableStock INT,         -- CurrentStock - ReservedStock
    SafetyStockLevel INT,       -- Minimum stock threshold
    ReorderPoint INT,           -- Trigger point for new orders
    MaxStockLevel INT,          -- Maximum warehouse capacity
    LastUpdated DATE,           -- Last inventory update
    AverageCost DECIMAL(10,2),  -- Weighted average unit cost
    Status STRING,              -- Active, Excess, Low Stock, Out of Stock
    CreatedBy STRING,           -- System user
    CreatedDate DATE       -- Record creation date
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

# CELL ********************

# 3. Create InventoryTransactions table for audit trail
TABLE_NAME = "InventoryTransactions"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    TransactionID STRING,
    ProductID STRING,           -- Links to existing Product table
    ProductName STRING,         -- Denormalized for usability
    ProductCategory STRING,     -- Camping, Kitchen, Ski
    WarehouseLocation STRING,   -- Foreign key to Warehouses.WarehouseID
    TransactionType STRING,     -- Receipt, Sale, Adjustment, Transfer
    TransactionDate DATE,       -- When transaction occurred
    Quantity INT,               -- Quantity moved (positive/negative)
    UnitCost DECIMAL(10,2),     -- Cost per unit at time of transaction
    TotalValue DECIMAL(10,2),   -- Total value of transaction
    ReferenceNumber STRING,     -- PO number, SO number, etc.
    ReasonCode STRING,          -- Reason for adjustment/transfer
    StockBefore INT,            -- Stock level before transaction
    StockAfter INT,             -- Stock level after transaction
    ProcessedBy STRING,         -- User who processed transaction
    Notes STRING,               -- Additional transaction details
    CreatedBy STRING,           -- System user
    CreatedDate DATE            -- Record creation date
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

# CELL ********************

# 4. Create PurchaseOrders table for procurement headers
TABLE_NAME = "PurchaseOrders"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    PurchaseOrderID STRING,
    PurchaseOrderNumber STRING, -- Unique PO identifier
    SupplierID STRING,          -- Links to Suppliers table
    SupplierName STRING,        -- Denormalized supplier name
    OrderDate DATE,             -- When order was placed
    ExpectedDeliveryDate DATE,  -- Expected delivery date
    ActualDeliveryDate DATE,    -- Actual delivery date (NULL if pending)
    Status STRING,              -- Pending, Shipped, Delivered, Cancelled
    TotalOrderValue DECIMAL(12,2), -- Total monetary value
    DeliveryLocation STRING,    -- Foreign key to Warehouses.WarehouseID
    OrderedBy STRING,           -- Employee who created order
    Priority STRING,            -- Low, Medium, High, Urgent
    Notes STRING,               -- Additional order notes
    CreatedBy STRING,           -- System user
    CreatedDate DATE            -- Record creation date
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

# CELL ********************

# 5. Create PurchaseOrderItems table for line item details
TABLE_NAME = "PurchaseOrderItems"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    PurchaseOrderItemID STRING,
    PurchaseOrderID STRING,     -- Links to PurchaseOrders table
    PurchaseOrderNumber STRING, -- Denormalized PO number
    ProductID STRING,           -- Links to Product table
    ProductName STRING,         -- Denormalized product name
    ProductCategory STRING,     -- Camping, Kitchen, Ski
    QuantityOrdered INT,        -- Quantity requested
    QuantityReceived INT,       -- Quantity actually received
    UnitCost DECIMAL(10,2),     -- Cost per unit
    LineTotal DECIMAL(12,2),    -- QuantityOrdered * UnitCost
    Status STRING,              -- Pending, Partial, Complete, Cancelled
    ExpectedDate DATE,          -- Expected receipt date for this line
    ReceivedDate DATE,          -- Actual receipt date (NULL if pending)
    Notes STRING,               -- Line-specific notes
    CreatedBy STRING,           -- System user
    CreatedDate DATE       -- Record creation date
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

# CELL ********************

# 6. Create DemandForecast table for predictive analytics
TABLE_NAME = "DemandForecast"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    ForecastID STRING,
    ProductID STRING,           -- Links to existing Product table
    ProductName STRING,         -- Denormalized for usability
    ProductCategory STRING,     -- Camping, Kitchen, Ski
    ForecastDate DATE,          -- Future date being predicted
    ForecastPeriod STRING,      -- Weekly, Monthly, Quarterly
    PredictedDemand INT,        -- Forecasted units needed
    ConfidenceLevel DECIMAL(5,2), -- 0-100% confidence score
    SeasonalMultiplier DECIMAL(5,2), -- Seasonal adjustment factor
    TrendDirection STRING,      -- Growing, Stable, Declining
    BaselineDemand INT,         -- Historical average demand
    MethodUsed STRING,          -- Forecast algorithm/method
    ForecastHorizon INT,        -- Days into future
    ActualDemand INT,           -- NULL until period completes
    AccuracyScore DECIMAL(5,2), -- NULL until actual vs predicted calculated
    CreatedBy STRING,           -- System user or model
    CreatedDate DATE       -- When forecast generated
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

print(f"🎉 {SCHEMA_NAME.upper()} DOMAIN COMPLETE!")
