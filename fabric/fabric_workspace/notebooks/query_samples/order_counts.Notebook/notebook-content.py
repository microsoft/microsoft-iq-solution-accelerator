# Fabric notebook source


# MARKDOWN ********************

# # Sales Channel Analytics
# 
# Query `sales.order` for channel performance metrics.

# CELL ********************

import pandas as pd
from pyspark.sql.functions import col, count, sum as spark_sum, avg, round as spark_round
import sempy.fabric as fabric

# Configuration
WORKSPACE_ID = fabric.get_notebook_workspace_id()
lakehouse_properties = mssparkutils.lakehouse.get("fabriciq_team_lake")
LAKEHOUSE_ID = lakehouse_properties.id

SCHEMA_NAME = "sales"
TABLE_NAME = "order"

TABLE_PATH = f"abfss://{WORKSPACE_ID}@onelake.dfs.fabric.microsoft.com/{LAKEHOUSE_ID}/Tables/{SCHEMA_NAME}/{TABLE_NAME}"

# Read the table
df = spark.read.format("delta").load(TABLE_PATH)

# Get total count for percentage calculation
total_count = df.count()

# Query using DataFrame API
result = df.groupBy("SalesChannelId") \
    .agg(
        count("*").alias("OrderCount"),
        spark_sum("OrderTotal").alias("TotalRevenue"),
        avg("OrderTotal").alias("AvgOrderValue")
    ) \
    .withColumn("Percentage", spark_round((col("OrderCount") * 100.0 / total_count), 2)) \
    .orderBy(col("TotalRevenue").desc())

# Convert to pandas for better formatting
pdf = result.toPandas()

# Format the numbers
pdf['TotalRevenue'] = pdf['TotalRevenue'].apply(lambda x: f"{x:,.2f}")
pdf['AvgOrderValue'] = pdf['AvgOrderValue'].apply(lambda x: f"{x:,.2f}")

print(pdf)
