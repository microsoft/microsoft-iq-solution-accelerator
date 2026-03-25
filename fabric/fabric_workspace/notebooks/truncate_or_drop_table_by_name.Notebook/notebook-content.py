# Fabric notebook source


# MARKDOWN ********************

# # Truncate or Drop Table
# 
# Simple utility to truncate or drop specific tables:
# - **Truncate**: Removes data, keeps table structure
# - **Drop**: Removes entire table

# MARKDOWN ********************

# ## Configuration
# 
# **Instructions**: Modify the variables below to specify your target table and operation.

# CELL ********************

# Configure your operation
SCHEMA_NAME = "schema_name"        # Schema name 
TABLE_NAME = "table_name"         # Table name 
OPERATION = "truncate"          # "truncate" or "drop"

print(f"Operation: {OPERATION.upper()} {SCHEMA_NAME}.{TABLE_NAME}")

# MARKDOWN ********************

# ## Available Schemas
# customer | product | sales | finance | inventory | supplychain
# 
# *Use `SHOW TABLES IN schema_name` to see tables in each schema*

# MARKDOWN ********************

# ## Execute Operation

# CELL ********************

# Simple validation
if OPERATION not in ["truncate", "drop"]:
    print("❌ Error: OPERATION must be 'truncate' or 'drop'")
else:
    print(f"✅ Ready to {OPERATION} {SCHEMA_NAME}.{TABLE_NAME}")

# CELL ********************

# Execute operation
try:
    if OPERATION == "truncate":
        spark.sql(f"TRUNCATE TABLE {SCHEMA_NAME}.{TABLE_NAME}")
        print(f"✅ Truncated {SCHEMA_NAME}.{TABLE_NAME} - data removed, table preserved")
        
    elif OPERATION == "drop":
        spark.sql(f"DROP TABLE IF EXISTS {SCHEMA_NAME}.{TABLE_NAME}")
        print(f"✅ Dropped {SCHEMA_NAME}.{TABLE_NAME} - table completely removed")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

# MARKDOWN ********************

# ## Verification (Optional)

# CELL ********************

# Quick verification
try:
    if OPERATION == "truncate":
        count = spark.sql(f"SELECT COUNT(*) as count FROM {SCHEMA_NAME}.{TABLE_NAME}").collect()[0]['count']
        print(f"📊 Table {SCHEMA_NAME}.{TABLE_NAME} now has {count} rows")
    elif OPERATION == "drop":
        tables = spark.sql(f"SHOW TABLES IN {SCHEMA_NAME}").filter(f"tableName = '{TABLE_NAME}'").count()
        print(f"📊 Table exists: {tables > 0}")
except Exception as e:
    print(f"Cannot verify: {str(e)}")
