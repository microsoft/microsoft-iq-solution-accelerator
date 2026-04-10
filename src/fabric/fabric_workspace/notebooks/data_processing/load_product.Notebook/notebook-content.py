# Fabric notebook source


# MARKDOWN ********************

# # Product Data Loading
# 
# This notebook loads all product-related CSV files from the lakehouse Files/data/product directory into Delta tables.
# 
# ## Tables to Load:
# 1. **Product** - Master product catalog with pricing, specifications, and lifecycle information
# 2. **ProductCategory** - Product category hierarchy with brand information and status

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
print(f"✅ Loading '{SCHEMA_NAME}' schema from: {DATA_PATH}")

# CELL ********************

# 1. Load Product Table
product_df = spark.read.csv("Files/data/product/Product_Samples_Combined.csv", header=True, inferSchema=False)
product_df = product_df \
    .withColumn("ListPrice", col("ListPrice").cast("decimal(18,2)")) \
    .withColumn("StandardCost", col("StandardCost").cast("decimal(18,2)")) \
    .withColumn("Weight", col("Weight").cast("decimal(18,3)")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date")) \
    .withColumn("SellStartDate", col("SellStartDate").cast("date")) \
    .withColumn("SellEndDate", col("SellEndDate").cast("date")) \
    .withColumn("UpdatedDate", col("UpdatedDate").cast("date"))
product_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.Product")
product_count = product_df.count()

# CELL ********************

# 2. Load ProductCategory Table
category_df = spark.read.csv("Files/data/product/ProductCategory_Samples_Combined.csv", header=True, inferSchema=False)
category_df = category_df \
    .withColumn("IsActive", col("IsActive").cast("boolean"))
category_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.ProductCategory")
category_count = category_df.count()

# CELL ********************

# Summary
total_records = product_count + category_count
print(f"✅ Product schema: 2 tables, {total_records:,} records loaded")
