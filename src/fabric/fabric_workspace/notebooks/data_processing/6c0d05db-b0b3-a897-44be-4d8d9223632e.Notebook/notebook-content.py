# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# # Customer Data Loading
# 
# This notebook loads all customer-related CSV files from the lakehouse Files/data/customer directory into Delta tables.
# 
# ## Tables to Load:
# 1. **Customer** - Master customer data with contact information and demographics
# 2. **CustomerAccount** - Customer account relationships and currency information
# 3. **CustomerRelationshipType** - Customer tier definitions and descriptions
# 4. **CustomerTradeName** - Business trade names and operating periods
# 5. **Location** - Customer addresses and geographic information

# CELL ********************

# Setup and Configuration
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Schema Configuration
SCHEMA_NAME = "customer"
DATA_PATH = "Files/data/customer"

# Ensure schema exists
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA_NAME}")
print(f"✅Loading '{SCHEMA_NAME}' schema from: {DATA_PATH}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# 1. Load Customer Table
customer_df = spark.read.csv(f"{DATA_PATH}/Customer_Samples.csv", header=True, inferSchema=False)
customer_df = customer_df \
    .withColumn("DateOfBirth", col("DateOfBirth").cast("date")) \
    .withColumn("CustomerEstablishedDate", col("CustomerEstablishedDate").cast("date")) \
    .withColumn("IsActive", col("IsActive").cast("boolean"))
customer_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.Customer")
customer_count = customer_df.count()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# 2. Load CustomerAccount Table (all STRING columns — no casts needed)
account_df = spark.read.csv(f"{DATA_PATH}/CustomerAccount_Samples.csv", header=True, inferSchema=False)
account_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.CustomerAccount")
account_count = account_df.count()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# 3. Load CustomerRelationshipType Table (all STRING columns — no casts needed)
relationship_df = spark.read.csv(f"{DATA_PATH}/CustomerRelationshipType_Samples.csv", header=True, inferSchema=False)
relationship_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.CustomerRelationshipType")
relationship_count = relationship_df.count()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# 4. Load CustomerTradeName Table
trade_name_df = spark.read.csv(f"{DATA_PATH}/CustomerTradeName_Samples.csv", header=True, inferSchema=False)
trade_name_df = trade_name_df \
    .withColumn("PeriodStartDate", col("PeriodStartDate").cast("date")) \
    .withColumn("PeriodEndDate", col("PeriodEndDate").cast("date"))
trade_name_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.CustomerTradeName")
trade_name_count = trade_name_df.count()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# 5. Load Location Table
location_df = spark.read.csv(f"{DATA_PATH}/Location_Samples.csv", header=True, inferSchema=False)
location_df = location_df \
    .withColumn("IsActive", col("IsActive").cast("boolean")) \
    .withColumn("Latitude", col("Latitude").cast("double")) \
    .withColumn("Longitude", col("Longitude").cast("double"))
location_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.Location")
location_count = location_df.count()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Summary
total_records = customer_count + account_count + relationship_count + trade_name_count + location_count
print(f"📊Customer schema: 5 tables, {total_records:,} records loaded")
print(f"   - Customer: {customer_count:,} records")
print(f"   - CustomerAccount: {account_count:,} records")
print(f"   - CustomerRelationshipType: {relationship_count:,} records")
print(f"   - CustomerTradeName: {trade_name_count:,} records")
print(f"   - Location: {location_count:,} records")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
