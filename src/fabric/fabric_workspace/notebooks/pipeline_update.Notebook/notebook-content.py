# Fabric notebook source


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

# MARKDOWN ********************

# ## Uncomment only if you also want to drop all scehame and tables

# CELL ********************

#%run drop_all_tables

# MARKDOWN ********************

# ### Create Scehama and Tables

# CELL ********************

#%run create_scheme_tables

# MARKDOWN ********************

# ### Load Data to all tables

# CELL ********************

#%run load_data_all_tables
