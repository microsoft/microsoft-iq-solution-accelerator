# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "e6cd0b76-50e8-498f-9cd0-89251fae70c2",
# META       "default_lakehouse_name": "miqsadata",
# META       "default_lakehouse_workspace_id": "27818fad-0450-42b9-a4a0-db84075ac8d7",
# META       "known_lakehouses": [
# META         {
# META           "id": "e6cd0b76-50e8-498f-9cd0-89251fae70c2"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# # Complete Data Pipeline
# 
# ## Overview
# This notebook orchestrates the complete data platform setup from scratch, including schema creation and data loading.
# 
# **Execution Order**: Create schemas and tables → Load all data
# 
# **Prerequisites**: 
# - Fabric lakehouse properly configured
# - PySpark session active

# CELL ********************

%run create_scheme_tables

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Load Data to all tables

# CELL ********************

%run load_data_all_tables

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
