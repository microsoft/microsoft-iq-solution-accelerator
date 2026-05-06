# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# # List Schemas and Tables in Fabric Lakehouse
# 
# Lists all schemas (databases) and their tables from the attached Fabric Lakehouse using Spark SQL.

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

# MARKDOWN ********************

