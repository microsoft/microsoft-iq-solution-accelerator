# Fabric notebook source


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

# MARKDOWN ********************

# ### Load Data to all tables

# CELL ********************

%run load_data_all_tables
