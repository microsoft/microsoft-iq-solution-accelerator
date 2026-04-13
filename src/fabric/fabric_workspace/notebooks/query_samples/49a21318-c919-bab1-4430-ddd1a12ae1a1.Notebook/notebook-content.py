# Fabric notebook source


# MARKDOWN ********************

# # Sales Channel Analytics
# 
# Query `sales.order` for channel performance metrics.

# CELL ********************

import pandas as pd
from pyspark.sql.functions import col, count, sum as spark_sum, avg, round as spark_round

# Read the table directly from the default lakehouse
# When a lakehouse is attached as default, you can access tables directly
df = spark.sql("SELECT * FROM sales.order")

# Alternative approach using table path:
# df = spark.table("sales.order")

# Get total count for percentage calculation
total_count = df.count()

# Query using DataFrame API
result = df.groupBy("ProductLineName") \
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
