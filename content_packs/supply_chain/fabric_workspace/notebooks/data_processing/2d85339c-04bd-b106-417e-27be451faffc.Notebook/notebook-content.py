# Fabric notebook source


# MARKDOWN ********************

# # Product Data Loading
# 
# This notebook loads all product-related CSV files from the lakehouse Files/data/product directory into Delta tables.
# 
# ## Tables to Load:
# 1. **ProductLine** - Product line definitions (Camping, Kitchen, Ski)
# 2. **Product** - Master product catalog with pricing, specifications, and lifecycle information
# 3. **ProductCategory** - Product category hierarchy with product line information and status
# 
# ## Schema Updates (Latest):
# - **ProductCategory**: Added ProductLineID (STRING), ProductLineName, CreatedBy, CreatedDate (DATE) 
# - **ProductCategory**: Renamed CategoryID → ProductCategoryID
# - **All ID columns**: Consistent STRING data type
# - Proper data type casting applied for all new columns

# CELL ********************

# Setup and Configuration
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Schema Configuration
SCHEMA_NAME = "product"
DATA_PATH = "Files/data/product"

# Ensure schema exists
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA_NAME}")
print(f"✅Loading '{SCHEMA_NAME}' schema from: {DATA_PATH}")

# CELL ********************

# 1. Load Product Table
product_df = spark.read.csv(f"{DATA_PATH}/Product_Samples_Combined.csv", header=True, inferSchema=False)
product_df = product_df \
    .withColumn("ProductID", col("ProductID").cast("string")) \
    .withColumn("ProductLineID", col("ProductLineID").cast("string")) \
    .withColumn("ListPrice", col("ListPrice").cast("double")) \
    .withColumn("StandardCost", col("StandardCost").cast("double")) \
    .withColumn("Weight", col("Weight").cast("double")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date")) \
    .withColumn("SellStartDate", col("SellStartDate").cast("date")) \
    .withColumn("SellEndDate", col("SellEndDate").cast("date")) \
    .withColumn("UpdatedDate", col("UpdatedDate").cast("date"))
product_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.Product")
product_count = product_df.count()

# CELL ********************

# 2. Load ProductCategory Table
category_df = spark.read.csv(f"{DATA_PATH}/ProductCategory_Samples_Combined.csv", header=True, inferSchema=False)
category_df = category_df \
    .withColumn("ProductLineID", col("ProductLineID").cast("string")) \
    .withColumn("IsActive", col("IsActive").cast("boolean")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date"))
category_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.ProductCategory")
category_count = category_df.count()

# CELL ********************

# 3. Load ProductLine Table
productline_df = spark.read.csv(f"{DATA_PATH}/ProductLine_Sample.csv", header=True, inferSchema=False)
productline_df = productline_df \
    .withColumn("ProductLineID", col("ProductLineID").cast("string")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date"))
productline_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.ProductLine")
productline_count = productline_df.count()

# CELL ********************

# Summary
total_records = productline_count + product_count + category_count
print(f"📊Product schema: 3 tables, {total_records:,} records loaded")
print(f"   - ProductLine: {productline_count:,} records")
print(f"   - Product: {product_count:,} records")
print(f"   - ProductCategory: {category_count:,} records")
