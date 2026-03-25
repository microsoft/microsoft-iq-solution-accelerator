# Fabric notebook source


# MARKDOWN ********************

# # Data Model for Product Dimentions. 
# 
# ## Schema Structure
# - **Product Catalog (2 tables)**: 
# - Product, Samples Ready: Product_Samples.csv
# - ProductCategory, Samples Ready: ProductCategory_Samples.csv

# MARKDOWN ********************


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
# Products - Product and ProductCategory, 2 Tables
################################################################################################

# 1. Create Product table
TABLE_NAME = "Product"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    ProductID STRING,
    ProductName STRING,
    ProductDescription STRING,
    BrandName STRING,
    ProductNumber STRING,
    Color STRING,
    ProductModel STRING,
    ProductCategoryID STRING,
    CategoryName STRING,
    ListPrice DECIMAL(18,2),
    StandardCost DECIMAL(18,2),
    Weight DECIMAL(18,3),
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

# 2. Create ProductCategory table
TABLE_NAME = "ProductCategory"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    CategoryID STRING,
    ParentCategoryID STRING,
    CategoryName STRING,
    CategoryDescription STRING,
    BrandName STRING,
    BrandLogoUrl STRING,
    IsActive BOOLEAN
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

print(f"🎉 {SCHEMA_NAME.upper()} DOMAIN COMPLETE!")
