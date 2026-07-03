# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "22222222-2222-2222-2222-222222222222",
# META       "default_lakehouse_name": "miqsadata",
# META       "default_lakehouse_workspace_id": "11111111-1111-1111-1111-111111111111",
# META       "known_lakehouses": [
# META         {
# META           "id": "22222222-2222-2222-2222-222222222222"
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
