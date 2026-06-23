# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# # Create Schemas and Tables 
# 
# ## Overview
# This notebook orchestrates the creation of all database schemas and tables for the business data platform.
# 
# **Execution Order**: Foundational domains first (customer, product) → Business processes (sales, finance) → Operations (inventory, supplychain)
# 
# **Prerequisites**: 
# - Fabric lakehouse properly configured
# - PySpark session active
# - Schema notebooks available in `../schema/` directory

# MARKDOWN ********************

# ### Create schema and tables for customer domain

# CELL ********************

%run model_customer

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Create schema and tables for product domain

# CELL ********************

%run model_product

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Create schema and tables for sales domain 

# CELL ********************

%run model_sales

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Create schema and tables for finance domain

# CELL ********************

%run model_finance

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Create schema and tables for inventory domain

# CELL ********************

%run model_inventory

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Create schema and tables for supplychain domain

# CELL ********************

%run model_supplychain

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Create schema and tables for shared domain

# CELL ********************

%run model_shared

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

print("🎉 All schemas and tables created successfully!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
