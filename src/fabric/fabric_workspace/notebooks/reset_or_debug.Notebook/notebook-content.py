# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# # Reset or Debug Tables
# 
# Debug utility for data pipeline maintenance:
# - **Truncate**: Clear data, keep table structure
# - **Load Data**: Reload fresh data into tables
# - **Drop**: Remove tables completely 
# - **Recreate**: Restore table schemas
# 
# ## How to Use
# 1. Uncomment the schema and tables you want to work with
# 2. Run truncate, load data, drop, or recreate sections as needed  
# 3. Change schema selection for different domains
# 
# ⚠️ **Warning**: Drop operations permanently delete tables and data.

# CELL ********************

# Uncomment the schema and tables you want to debug

# SCHEMA_NAME = "customer"
# TABLES = ["Customer", "CustomerTradeName", "CustomerRelationshipType", "Location", "CustomerAccount"]

# SCHEMA_NAME = "product"
# TABLES = ["ProductLine", "Product", "ProductCategory"]

# SCHEMA_NAME = "sales"
# TABLES = ["Order", "OrderLine", "OrderPayment"]

# SCHEMA_NAME = "finance"  
# TABLES = ["invoice", "account", "payment"]

# SCHEMA_NAME = "inventory"
# TABLES = ["Warehouses", "Inventory", "InventoryTransactions", "PurchaseOrders", "PurchaseOrderItems", "DemandForecast"]

# SCHEMA_NAME = "supplychain"
# TABLES = ["Suppliers", "ProductSuppliers", "SupplyChainEvents", "SupplyChainEventImpacts"]

# SCHEMA_NAME = "shared"
# TABLES = ["DimDate"]

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Truncate Tables

# CELL ********************

for table in TABLES:
    try:
        spark.sql(f"TRUNCATE TABLE {SCHEMA_NAME}.{table}")
        print(f"✅ Truncated {table}")
    except Exception as e:
        print(f"⚠️ Skipped {table} (truncate not supported)")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Load Data - uncomment and swap the code below if you want to run a different model

# CELL ********************

# %run load_customer

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Drop Tables

# CELL ********************

# Do run this if you just need to reload data
# Run this only if the schema has been updated

for table in TABLES:
    try:
        spark.sql(f"DROP TABLE {SCHEMA_NAME}.{table}")
        print(f"✅ Dropped {table}")
    except Exception as e:
        print(f"⚠️ Skipped {table} (drop failed: {str(e)[:50]}...)")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Recreate Tables only if needed - and swap the code below with your own model

# CELL ********************

# %run model_customer

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
