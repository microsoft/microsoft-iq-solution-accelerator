# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "1650c6ba-a2fa-44f8-ba66-d4643da39fae",
# META       "default_lakehouse_name": "fabriciq_team_lake",
# META       "default_lakehouse_workspace_id": "27818fad-0450-42b9-a4a0-db84075ac8d7",
# META       "known_lakehouses": [
# META         {
# META           "id": "1650c6ba-a2fa-44f8-ba66-d4643da39fae"
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
# **Execution Order**: Clean environment → Create schemas and tables → Load all data
# 
# **Prerequisites**: 
# - Fabric lakehouse properly configured
# - PySpark session active

# MARKDOWN ********************

# ## Uncomment only if you need to clean up tables

# CELL ********************

%run truncate_all_tables

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Uncomment only if you also want to drop all scehame and tables

# CELL ********************

%run drop_all_tables

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Create Scehama and Tables

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
