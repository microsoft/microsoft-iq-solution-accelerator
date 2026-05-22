# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# ## Sales Analytics by ProductLineName
# 
# Query `sales.order` for channel performance metrics.

# CELL ********************

import pandas as pd
from pyspark.sql.functions import col, count, sum as spark_sum, avg, round as spark_round
import sempy.fabric as fabric

# Configuration
WORKSPACE_ID = fabric.get_notebook_workspace_id()
lakehouse_properties = mssparkutils.lakehouse.get()  # Gets the default attached lakehouse
LAKEHOUSE_ID = lakehouse_properties.id

SCHEMA_NAME = "sales"
TABLE_NAME = "order"

TABLE_PATH = f"abfss://{WORKSPACE_ID}@onelake.dfs.fabric.microsoft.com/{LAKEHOUSE_ID}/Tables/{SCHEMA_NAME}/{TABLE_NAME}"

# Read the table
df = spark.read.format("delta").load(TABLE_PATH)

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

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Get Data Summary

# CELL ********************

import os
import pandas as pd

root = "/lakehouse/default/Tables"
EXCLUDE_EXTENSIONS = (".gz", ".delta")
EXCLUDE_ENTRIES = {"_delta_log", "_committed", "_started"}

results = []

for schema in sorted(os.listdir(root)):
    schema_path = os.path.join(root, schema)
    if not os.path.isdir(schema_path):
        continue
    print(f"\n📁 {schema}")
    for table in sorted(os.listdir(schema_path)):
        if table in EXCLUDE_ENTRIES or any(table.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
            continue
        try:
            row_count = spark.sql(f"SELECT COUNT(*) FROM `{schema}`.`{table}`").collect()[0][0]
        except Exception as e:
            row_count = f"ERROR ({e})"
        results.append((schema, table, row_count))
        print(f"   {table}: {row_count:,}" if isinstance(row_count, int) else f"   {table}: {row_count}")

summary_df = pd.DataFrame(results, columns=["Schema", "Table", "Row Count"])
display(summary_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# List Schema and Tables

# CELL ********************

import os

root = "/lakehouse/default/Tables"
EXCLUDE_EXTENSIONS = (".gz", ".delta")
EXCLUDE_ENTRIES = {"_delta_log", "_committed", "_started"}

for schema in sorted(os.listdir(root)):
    schema_path = os.path.join(root, schema)
    if not os.path.isdir(schema_path):
        continue
    print(f"\n=== SCHEMA: {schema} ===")
    for table in sorted(os.listdir(schema_path)):
        if table in EXCLUDE_ENTRIES or any(table.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
            continue
        print(f"  - {table}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
