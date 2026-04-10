# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# # Load Data All Tables
# 
# ## Overview
# This notebook orchestrates the loading of all CSV data files into Delta tables for the business data platform.
# 
# **Execution Order**: Foundational domains first (customer, product) → Business processes (sales, finance) → Operations (inventory, supplychain)
# 
# **Prerequisites**: 
# - Fabric lakehouse properly configured
# - PySpark session active

# MARKDOWN ********************

# ## Prepare Clean Environment
# 
# **⚠️ Warning**: Uncomment the line below only if you want to completely reload all data.
# 
# **Recommendation**: Run selectively for development/testing environments only.

# CELL ********************

# %run truncate_all_tables

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Load data for customer domain

# CELL ********************

%run load_customer

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Load data for product domain

# CELL ********************

%run load_product

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Load data for sales domain 

# CELL ********************

%run load_sales

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Load data for finance domain

# CELL ********************

%run load_finance

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Load data for inventory domain

# CELL ********************

%run load_inventory

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Load data for supplychain domain

# CELL ********************

%run load_supplychain

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from datetime import datetime
from IPython.display import display, HTML

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print (f"✅ Data Loading Complete - Completed at: {timestamp}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
