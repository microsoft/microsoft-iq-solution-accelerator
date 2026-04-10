# Fabric notebook source


# MARKDOWN ********************

# #  Data Model for Sales
# 
# ## Overview
# This notebook creates Sales domain tables that integrate with shared data.
# 
# ## Schema Structure
# - **Sales Domain**: 3 tables (Order, OrderLine, OrderPayment)
# - **Integration**: Links to shared Customer, Product, Location tables
# 
# ---

# CELL ********************

################################################################################################
# Schema Configuration - You can define different value here
################################################################################################

# Schema Configuration
SCHEMA_NAME = "sales"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA_NAME}")
print(f"✅ {SCHEMA_NAME} schema ready!")

# CELL ********************

################################################################################################
# SALES DOMAIN TABLES - Fabric Channel
################################################################################################

# 1. Create Order table
# Need to generate orderlines first and then sum them into Order 
TABLE_NAME = "Order"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    OrderID STRING,         -- Unique identifer like UUID
    SalesChannelID STRING,  -- Values: Camping, Kitchen, Ski
    OrderNumber STRING,     -- Customer-facing order number
    CustomerID STRING,      -- FK to Customer 
    CustomerAccountID STRING,
    OrderDate DATE,
    OrderStatus STRING,
    SubTotal DECIMAL(18,2),
    TaxAmount DECIMAL(18,2),
    OrderTotal DECIMAL(18,2),
    PaymentMethod STRING,
    IsoCurrencyCode STRING,
    CreatedBy STRING 
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

# 2. Create OrderLine table
# If the customer ordered 3 products, there will be three records of orderline
# Use a tax rate of 5% across the orderline items 

TABLE_NAME = "OrderLine"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    OrderID STRING,             -- FK to Order table
    OrderLineNumber INT,        -- incremental number for each line item, like 1, 2, 3.
    ProductID STRING,           -- FK to Product
    ProductName STRING,
    Quantity INT,
    UnitPrice DECIMAL(18,2),
    LineTotal DECIMAL(18,2),
    DiscountAmount DECIMAL(18,2), 
    TaxAmount DECIMAL(18,2)
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

# 3. Create OrderPayment table
TABLE_NAME = "OrderPayment"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    OrderID STRING,       -- FK to Order table
    PaymentMethod STRING,      -- VISA, MC, Discover, PayPal.
    TransactionID STRING     --UUID for Payment Transaction
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

print(f"🎉 {SCHEMA_NAME.upper()} DOMAIN COMPLETE!")
