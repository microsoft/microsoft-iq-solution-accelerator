# Fabric notebook source


# MARKDOWN ********************

# # Data Model for Product Dimensions
# 
# ## Schema Structure
# **3 tables**: ProductLine, Product, ProductCategory
# 
# ## Data Sources
# - ProductLine_Sample.csv
# - Product_Samples_Combined.csv  
# - ProductCategory_Samples_Combined.csv

# CELL ********************

################################################################################################
# Schema Configuration - You can define different value here
################################################################################################

# Schema Configuration
SCHEMA_NAME = "product"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA_NAME}")
print(f"✅ {SCHEMA_NAME} schema ready!")

# CELL ********************

################################################################################################
# Products - ProductLine, Product and ProductCategory, 3 Tables
################################################################################################

# 1. Create ProductLine table
TABLE_NAME = "ProductLine"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    ProductLineID STRING NOT NULL,
    ProductLineName STRING NOT NULL,
    Description STRING,
    CreatedBy STRING,
    CreatedDate DATE
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")


# 2. Create Product table
TABLE_NAME = "Product"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    ProductID STRING,
    ProductLineID STRING,       -- Added
    ProductName STRING,
    ProductDescription STRING,
    -- BrandName STRING,         -- Deleted 
    ProductNumber STRING,
    Color STRING,
    ProductModel STRING,
    ProductCategoryID STRING,
    CategoryName STRING,
    ListPrice DOUBLE,
    StandardCost DOUBLE,
    Weight DOUBLE,
    WeightUom STRING,     -- kg, lb, oz
    ProductStatus STRING, -- active, inactive, discontinued
    CreatedDate DATE,
    SellStartDate DATE,
    SellEndDate DATE,
    IsoCurrencyCode STRING,
    UpdatedDate DATE,
    CreatedBy STRING,
    UpdatedBy STRING
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

# 3. Create ProductCategory table
TABLE_NAME = "ProductCategory"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    -- ParentCategoryID STRING,   -- deleted 
    -- BrandName STRING,          -- deleted
    -- BrandLogoUrl STRING,       -- deleted
    ProductCategoryID STRING NOT NULL,    -- Changed from CategoryID to ProductCategoryID
    ProductLineID STRING,                 -- FIXED: Changed from INT to STRING
    ProductLineName STRING,               -- Camping, Kitchen, Ski
    CategoryName STRING NOT NULL,
    CategoryDescription STRING,
    IsActive BOOLEAN,
    CreatedBy STRING,              -- System
    CreatedDate DATE               -- 1/1/2018
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

print(f"🎉 {SCHEMA_NAME.upper()} DOMAIN COMPLETE!")
