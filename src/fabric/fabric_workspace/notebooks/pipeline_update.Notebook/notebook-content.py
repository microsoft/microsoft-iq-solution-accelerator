# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
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

#%run truncate_all_tables

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Uncomment only if you also want to drop all scehame and tables

# CELL ********************

#%run drop_all_tables

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Create Scehama and Tables

# CELL ********************

#%run create_scheme_tables

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Load Data to all tables

# CELL ********************

#%run load_data_all_tables

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
