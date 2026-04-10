# Fabric notebook source


# MARKDOWN ********************

# # Supply Chain Data Model - Suppliers & Disruptions
# 
# ## Schema Structure
# - **Suppliers Table**: Master data for product suppliers/distributors with backup relationships
# - **ProductSuppliers Table**: Links products to suppliers with pricing and terms
# - **SupplyChainEvents Table**: Consolidated disruption events and their impacts (merged from 2 tables)
# - Supports Primary/Backup supplier hierarchies and streamlined disruption analysis

# CELL ********************

################################################################################################
# Schema Configuration - You can define different value here
################################################################################################

# Schema Configuration
SCHEMA_NAME = "supplychain"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA_NAME}")
print(f"✅ {SCHEMA_NAME} schema ready!")

# CELL ********************

################################################################################################
# Supply Chain Domain - Suppliers and Product-Supplier Mapping Tables
################################################################################################

# CELL ********************

# Create all Supply Chain tables - Suppliers, ProductSuppliers, and SupplyChainEvents

# 1. Create Suppliers table
TABLE_NAME = "Suppliers"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    SupplierID STRING,
    SupplierName STRING,
    SupplierType STRING,  -- Primary, Backup, Emergency
    Status STRING,        -- Active, Disrupted, Inactive  
    ProductCategory STRING, -- Camping, Kitchen, Ski, Multi
    PrimarySupplierID STRING,  -- NULL for primary suppliers
    LeadTimeDays INT,     -- Standard delivery time
    ReliabilityScore INT, -- 0-100 performance rating
    Location STRING,      -- City, Country
    ContactEmail STRING,  -- Primary contact
    CreatedBy STRING,     -- System user
    CreatedDate DATE      -- Record creation
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

# 2. Create ProductSuppliers mapping table
TABLE_NAME = "ProductSuppliers"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    ProductSupplierID STRING,
    ProductID STRING,         -- Links to existing Product table
    ProductName STRING,       -- Denormalized for usability
    ProductCategory STRING,   -- Camping, Kitchen, Ski
    SupplierID STRING,        -- Links to Suppliers table
    SupplierName STRING,     -- Denormalized for usability
    SupplierProductCode STRING, -- Supplier's internal SKU
    WholesaleCost DECIMAL(10,2), -- Cost per unit
    MinOrderQuantity INT,    -- Minimum order size
    MaxOrderQuantity INT,    -- Maximum order size (NULL = no limit)
    LeadTimeDays INT,        -- Product-specific lead time
    Status STRING,           -- Active, Discontinued
    CreatedBy STRING,        -- System user
    CreatedDate DATE         -- Record creation
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

# 3. Create SupplyChainEvents consolidated table
# Combines disruption events and their impacts in single table
TABLE_NAME = "SupplyChainEvents"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    EventID STRING,
    DisruptionType STRING,     -- Weather, Political, Economic, Pandemic, Transport, Supplier
    EventName STRING,          -- Short descriptive name
    Description STRING,        -- Detailed description
    Severity STRING,           -- Low, Medium, High, Critical
    Status STRING,             -- Active, Monitoring, Resolved
    StartDate DATE,            -- When disruption began
    EndDate DATE,              -- When disruption resolved (NULL if ongoing)
    GeographicArea STRING,     -- Affected region/country
    IndustryImpact STRING,     -- Outdoor, Retail, Manufacturing, Logistics
    PredictedDuration INT,     -- Expected duration in days
    ActualDuration INT,        -- Actual duration in days (NULL if ongoing)
    AlertLevel STRING,         -- Green, Yellow, Orange, Red
    ReportedBy STRING,         -- Who reported the disruption
    -- Impact Details (nullable for general events)
    SupplierID STRING,        -- Specific supplier affected (NULL for general events)
    ProductCategory STRING,   -- Affected category: Camping, Kitchen, Ski (NULL for general)
    ImpactLevel STRING,       -- None, Low, Medium, High
    DeliveryDelay INT,        -- Additional days delay caused
    CostIncrease DECIMAL(5,2), -- % increase in costs (0.00-100.00)
    AlternativeAction STRING,  -- Action taken to mitigate
    EstimatedRevenueImpact DECIMAL(12,2), -- Financial impact estimate
    CreatedBy STRING,         -- System user
    CreatedDate DATE          -- Record creation
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

print(f"🎉 {SCHEMA_NAME.upper()} DOMAIN COMPLETE!")
