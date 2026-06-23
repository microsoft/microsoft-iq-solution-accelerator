# Fabric notebook source


# MARKDOWN ********************

# # Sales Data Loading
# 
# This notebook loads all sales-related CSV files from three product line directories into Delta tables.
# 
# ## Data Sources:
# - **Camping**: Files/data/sales/camping/
# - **Kitchen**: Files/data/sales/kitchen/
# - **Ski**: Files/data/sales/ski/
# 
# ## Tables to Load:
# 1. **Order** - Order headers from all three product lines
# 2. **OrderLine** - Order line items from all three product lines  
# 3. **OrderPayment** - Payment information from all three product lines

# CELL ********************

# Setup and Configuration
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Schema Configuration
SCHEMA_NAME = "sales"
DATA_PATH = "Files/data/sales"

# Product line paths
PRODUCT_LINES = ['camping', 'kitchen', 'ski']

# Ensure schema exists
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA_NAME}")
print(f"✅Loading '{SCHEMA_NAME}' schema from {len(PRODUCT_LINES)} product lines: {', '.join(PRODUCT_LINES)}")

# CELL ********************

# 1. Load Order Table from All Product Lines
order_dfs = []
for product_line in PRODUCT_LINES:
    df = spark.read.csv(f"{DATA_PATH}/{product_line}/Order_Samples_{product_line.title()}.csv", header=True, inferSchema=False)
    df = df \
        .withColumn("OrderDate", col("OrderDate").cast("date")) \
        .withColumn("SubTotal", col("SubTotal").cast("double")) \
        .withColumn("TaxAmount", col("TaxAmount").cast("double")) \
        .withColumn("OrderTotal", col("OrderTotal").cast("double"))
    order_dfs.append(df)

combined_orders_df = order_dfs[0]
for df in order_dfs[1:]:
    combined_orders_df = combined_orders_df.union(df)

combined_orders_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.Order")
orders_count = combined_orders_df.count()

# CELL ********************

# 2. Load OrderLine Table from All Product Lines
orderline_dfs = []
for product_line in PRODUCT_LINES:
    df = spark.read.csv(f"{DATA_PATH}/{product_line}/OrderLine_Samples_{product_line.title()}.csv", header=True, inferSchema=False)
    df = df \
        .withColumn("OrderLineNumber", col("OrderLineNumber").cast("int")) \
        .withColumn("Quantity", col("Quantity").cast("int")) \
        .withColumn("UnitPrice", col("UnitPrice").cast("double")) \
        .withColumn("LineTotal", col("LineTotal").cast("double")) \
        .withColumn("DiscountAmount", col("DiscountAmount").cast("double")) \
        .withColumn("TaxAmount", col("TaxAmount").cast("double"))
    orderline_dfs.append(df)

combined_orderlines_df = orderline_dfs[0]
for df in orderline_dfs[1:]:
    combined_orderlines_df = combined_orderlines_df.union(df)

combined_orderlines_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.OrderLine")
orderlines_count = combined_orderlines_df.count()


# CELL ********************

# 3. Load OrderPayment Table from All Product Lines
orderpayment_dfs = []
for product_line in PRODUCT_LINES:
    if product_line == "camping":
        file_name = "OrderPayment_Camping.csv"
    elif product_line == "kitchen":
        file_name = "OrderPayment_Kitchen.csv"
    else:  # ski
        file_name = "OrderPayment_Ski.csv"

    df = spark.read.csv(f"{DATA_PATH}/{product_line}/{file_name}", header=True, inferSchema=False)
    orderpayment_dfs.append(df)

combined_payments_df = orderpayment_dfs[0]
for df in orderpayment_dfs[1:]:
    combined_payments_df = combined_payments_df.union(df)

combined_payments_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.OrderPayment")
payments_count = combined_payments_df.count()

# CELL ********************

# Summary
total_records = orders_count + orderlines_count + payments_count
print(f"📊Sales schema: 3 tables, {total_records:,} records loaded")
