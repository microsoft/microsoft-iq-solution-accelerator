# Fabric notebook source


# MARKDOWN ********************

# # Inventory Data Loading
# 
# This notebook loads all inventory-related CSV files from the lakehouse Files/data/inventory directory into Delta tables.
# 
# ## Tables to Load:
# 1. **Warehouses** - Distribution centers and storage facilities with operational details
# 2. **Inventory** - Current stock levels and warehouse information
# 3. **InventoryTransactions** - All stock movements and adjustments
# 4. **PurchaseOrders** - Purchase order headers with supplier information
# 5. **PurchaseOrderItems** - Purchase order line items with product details
# 6. **DemandForecast** - Predictive analytics for future demand planning

# CELL ********************

# Setup and Configuration
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Schema Configuration
SCHEMA_NAME = "inventory"
DATA_PATH = "Files/data/inventory"

# Ensure schema exists
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA_NAME}")
print(f"✅ Loading '{SCHEMA_NAME}' schema from: {DATA_PATH}")

# CELL ********************

# 1. Load Warehouses Table
warehouses_df = spark.read.csv(f"{DATA_PATH}/Warehouses.csv", header=True, inferSchema=False)
warehouses_df = warehouses_df \
    .withColumn("Priority", col("Priority").cast("decimal(3,2)")) \
    .withColumn("MaxCapacity", col("MaxCapacity").cast("int")) \
    .withColumn("StaffCount", col("StaffCount").cast("int")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date")) \
    .withColumn("LastUpdated", col("LastUpdated").cast("date"))
warehouses_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.Warehouses")
warehouses_count = warehouses_df.count()

# CELL ********************

# 2. Load Inventory Table
inventory_df = spark.read.csv(f"{DATA_PATH}/Inventory.csv", header=True, inferSchema=False)
inventory_df = inventory_df \
    .withColumn("CurrentStock", col("CurrentStock").cast("int")) \
    .withColumn("ReservedStock", col("ReservedStock").cast("int")) \
    .withColumn("AvailableStock", col("AvailableStock").cast("int")) \
    .withColumn("SafetyStockLevel", col("SafetyStockLevel").cast("int")) \
    .withColumn("ReorderPoint", col("ReorderPoint").cast("int")) \
    .withColumn("MaxStockLevel", col("MaxStockLevel").cast("int")) \
    .withColumn("AverageCost", col("AverageCost").cast("decimal(10,2)")) \
    .withColumn("LastUpdated", col("LastUpdated").cast("date")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date"))
inventory_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.Inventory")
inventory_count = inventory_df.count()

# CELL ********************

# 3. Load InventoryTransactions Table
transactions_df = spark.read.csv(f"{DATA_PATH}/InventoryTransactions.csv", header=True, inferSchema=False)
transactions_df = transactions_df \
    .withColumn("Quantity", col("Quantity").cast("int")) \
    .withColumn("UnitCost", col("UnitCost").cast("decimal(10,2)")) \
    .withColumn("TotalValue", col("TotalValue").cast("decimal(10,2)")) \
    .withColumn("StockBefore", col("StockBefore").cast("int")) \
    .withColumn("StockAfter", col("StockAfter").cast("int")) \
    .withColumn("TransactionDate", col("TransactionDate").cast("date")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date"))
transactions_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.InventoryTransactions")
transactions_count = transactions_df.count()

# CELL ********************

# 4. Load PurchaseOrders Table
orders_df = spark.read.csv(f"{DATA_PATH}/PurchaseOrders.csv", header=True, inferSchema=False)
orders_df = orders_df \
    .withColumn("TotalOrderValue", col("TotalOrderValue").cast("decimal(12,2)")) \
    .withColumn("OrderDate", col("OrderDate").cast("date")) \
    .withColumn("ExpectedDeliveryDate", col("ExpectedDeliveryDate").cast("date")) \
    .withColumn("ActualDeliveryDate", col("ActualDeliveryDate").cast("date")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date"))
orders_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.PurchaseOrders")
orders_count = orders_df.count()

# CELL ********************

# 5. Load PurchaseOrderItems Table
order_items_df = spark.read.csv(f"{DATA_PATH}/PurchaseOrderItems.csv", header=True, inferSchema=False)
order_items_df = order_items_df \
    .withColumn("QuantityOrdered", col("QuantityOrdered").cast("int")) \
    .withColumn("QuantityReceived", col("QuantityReceived").cast("int")) \
    .withColumn("UnitCost", col("UnitCost").cast("decimal(10,2)")) \
    .withColumn("LineTotal", col("LineTotal").cast("decimal(12,2)")) \
    .withColumn("ExpectedDate", col("ExpectedDate").cast("date")) \
    .withColumn("ReceivedDate", col("ReceivedDate").cast("date")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date"))
order_items_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.PurchaseOrderItems")
order_items_count = order_items_df.count()

# CELL ********************

# 6. Load DemandForecast Table
# need to drop two fields that were nto in the model: SalesTrendMultiplier, CompoundTrendMultiplier
forecast_df = spark.read.csv(f"{DATA_PATH}/DemandForecast.csv", header=True, inferSchema=False)
forecast_df = forecast_df \
    .withColumn("PredictedDemand", col("PredictedDemand").cast("int")) \
    .withColumn("BaselineDemand", col("BaselineDemand").cast("int")) \
    .withColumn("ForecastHorizon", col("ForecastHorizon").cast("int")) \
    .withColumn("ActualDemand", col("ActualDemand").cast("int")) \
    .withColumn("ConfidenceLevel", col("ConfidenceLevel").cast("decimal(5,2)")) \
    .withColumn("SeasonalMultiplier", col("SeasonalMultiplier").cast("decimal(5,2)")) \
    .withColumn("AccuracyScore", col("AccuracyScore").cast("decimal(5,2)")) \
    .withColumn("ForecastDate", col("ForecastDate").cast("date")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date")) \
    .drop("SalesTrendMultiplier", "CompoundTrendMultiplier")
forecast_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.DemandForecast")
forecast_count = forecast_df.count()


# CELL ********************

# Summary
total_records = warehouses_count + inventory_count + transactions_count + orders_count + order_items_count + forecast_count
print(f"✅ Inventory schema: 6 tables, {total_records:,} records loaded")
