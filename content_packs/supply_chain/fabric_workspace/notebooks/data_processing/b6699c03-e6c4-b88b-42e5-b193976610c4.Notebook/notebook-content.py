# Fabric notebook source


# MARKDOWN ********************

# # Supply Chain Data Loading
# 
# This notebook loads all supply chain-related CSV files from the lakehouse Files/data/supplychain directory into Delta tables.
# 
# ## Tables to Load:
# 1. **Suppliers** - Master supplier data with backup relationships and performance metrics
# 2. **ProductSuppliers** - Product-supplier mappings with pricing and order parameters (placeholder - no CSV file)
# 3. **SupplyChainEvents** - Supply chain disruption events tracking
# 4. **SupplyChainEventImpacts** - Detailed impact analysis for each event

# CELL ********************

# Setup and Configuration
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Schema Configuration
SCHEMA_NAME = "supplychain"
DATA_PATH = "Files/data/supplychain"

# Ensure schema exists
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA_NAME}")
print(f"✅Loading '{SCHEMA_NAME}' schema from: {DATA_PATH}")

# CELL ********************

# 1. Load Suppliers Table
suppliers_df = spark.read.csv(f"{DATA_PATH}/Suppliers_Sample.csv", header=True, inferSchema=False)
suppliers_df = suppliers_df \
    .withColumn("LeadTimeDays", col("LeadTimeDays").cast("int")) \
    .withColumn("ReliabilityScore", col("ReliabilityScore").cast("int")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date"))
suppliers_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.Suppliers")
suppliers_count = suppliers_df.count()

# CELL ********************

# 2. Load ProductSuppliers Table
product_suppliers_df = spark.read.csv(f"{DATA_PATH}/ProductSuppliers_Sample.csv", header=True, inferSchema=False)
product_suppliers_df = product_suppliers_df \
    .withColumn("WholesaleCost", col("WholesaleCost").cast("double")) \
    .withColumn("MinOrderQuantity", col("MinOrderQuantity").cast("int")) \
    .withColumn("MaxOrderQuantity", col("MaxOrderQuantity").cast("int")) \
    .withColumn("LeadTimeDays", col("LeadTimeDays").cast("int")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date"))
product_suppliers_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.ProductSuppliers")
product_suppliers_count = product_suppliers_df.count()

# CELL ********************

# 3. Load SupplyChainEvents Table
supply_chain_events_df = spark.read.csv(f"{DATA_PATH}/SupplyChainEvents_Sample.csv", header=True, inferSchema=False)
supply_chain_events_df = supply_chain_events_df \
    .withColumn("StartDate", col("StartDate").cast("date")) \
    .withColumn("EndDate", col("EndDate").cast("date")) \
    .withColumn("PredictedDuration", col("PredictedDuration").cast("int")) \
    .withColumn("ActualDuration", col("ActualDuration").cast("double")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date"))
supply_chain_events_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.SupplyChainEvents")
events_count = supply_chain_events_df.count()

# CELL ********************

# 4. Load SupplyChainEventImpacts Table
event_impacts_df = spark.read.csv(f"{DATA_PATH}/SupplyChainEventImpacts_Sample.csv", header=True, inferSchema=False)
event_impacts_df = event_impacts_df \
    .withColumn("DeliveryDelay", col("DeliveryDelay").cast("int")) \
    .withColumn("CostIncrease", col("CostIncrease").cast("double")) \
    .withColumn("EstimatedRevenueImpact", col("EstimatedRevenueImpact").cast("double")) \
    .withColumn("CreatedDate", col("CreatedDate").cast("date"))
event_impacts_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.SupplyChainEventImpacts")
impacts_count = event_impacts_df.count()

# CELL ********************

# Summary
total_records = suppliers_count + product_suppliers_count + events_count + impacts_count
print(f"📊Supplychain schema: 4 tables, {total_records:,} records loaded")
print(f"   - Suppliers: {suppliers_count:,} records")
print(f"   - ProductSuppliers: {product_suppliers_count:,} records")
print(f"   - SupplyChainEvents: {events_count:,} records")
print(f"   - SupplyChainEventImpacts: {impacts_count:,} records")
