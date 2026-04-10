# Fabric notebook source


# MARKDOWN ********************

# # Data Summary — Row Counts by Schema and Table
# 
# Iterates over every schema (database) and every table in the attached Fabric Lakehouse and prints the row count for each one.
# 
# **Output format:** `Schema:<schema>, Table:<table>, # records: <rowcount>`

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

