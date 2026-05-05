# Fabric notebook source


# MARKDOWN ********************

# # Supply Chain Data Model - Suppliers & Disruptions
# 
# ## Schema Structure
# - **Suppliers Table**: Master data for product suppliers/distributors with backup relationships
# - **ProductSuppliers Table**: Links products to suppliers with pricing and terms
# - **SupplyChainEvents Table**: Disruption events with basic event information
# - **SupplyChainEventImpacts Table**: Detailed impact analysis for each event
# - Supports Primary/Secondary supplier hierarchies and comprehensive disruption tracking

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
    SupplierType STRING,  -- Primary, Secondary, Emergency
    Status STRING,        -- Active, Disrupted, Inactive  
    ProductLineName STRING, -- Camping, Kitchen, Ski, Multi
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
    ProductLineName STRING,   -- Camping, Kitchen, Ski
    SupplierID STRING,        -- Links to Suppliers table
    SupplierName STRING,     -- Denormalized for usability
    SupplierProductCode STRING, -- Supplier's internal SKU
    WholesaleCost DOUBLE, -- Cost per unit
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

# 3. Create SupplyChainEvents table (matches CSV structure)
TABLE_NAME = "SupplyChainEvents"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    EventID STRING,
    SupplierID STRING,        -- Supplier affected by the event
    DisruptionType STRING,    -- Weather, Political, Economic, Pandemic, Transport, Supplier
    EventName STRING,         -- Short descriptive name
    Description STRING,       -- Detailed description
    Severity STRING,          -- Low, Medium, High, Critical
    Status STRING,            -- Active, Monitoring, Resolved
    StartDate DATE,           -- When disruption began
    EndDate DATE,             -- When disruption resolved (NULL if ongoing)
    GeographicArea STRING,    -- Affected region/country
    IndustryImpact STRING,    -- Outdoor, Retail, Manufacturing, Logistics
    PredictedDuration INT,    -- Expected duration in days
    ActualDuration DOUBLE, -- Actual duration in days (NULL if ongoing)
    AlertLevel STRING,        -- Green, Yellow, Orange, Red
    ReportedBy STRING,        -- Who reported the disruption
    CreatedBy STRING,         -- System user
    CreatedDate DATE          -- Record creation
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

# 4. Create SupplyChainEventImpacts table (separate impact details)
TABLE_NAME = "SupplyChainEventImpacts"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    ImpactID STRING,
    EventID STRING,           -- Links to SupplyChainEvents
    SupplierID STRING,        -- Supplier affected
    ProductLineName STRING,   -- Affected category: Camping, Kitchen, Ski
    ImpactLevel STRING,       -- None, Low, Medium, High
    DeliveryDelay INT,        -- Additional days delay caused
    CostIncrease DOUBLE, -- % increase in costs (0.00-100.00)
    AlternativeAction STRING, -- Action taken to mitigate
    EstimatedRevenueImpact DOUBLE, -- Financial impact estimate
    CreatedBy STRING,         -- System user
    CreatedDate DATE          -- Record creation
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

print(f"🎉 {SCHEMA_NAME.upper()} DOMAIN COMPLETE!")
