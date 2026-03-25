# Fabric notebook source


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

# ## Prepare Clean Environment
# 
# **⚠️ Warning**: Uncomment the lines below only if you want to completely reset all schemas and data.
# 
# - `truncate_all_tables`: Removes all data but keeps table structures
# - `delete_all_schemas`: Drops all schemas and tables entirely
# 
# **Recommendation**: Run selectively for development/testing environments only.

# CELL ********************

# %run truncate_all_tables
# %run delete_all_schemas

# MARKDOWN ********************

# ### Create schema and tables for customer domain

# CELL ********************

%run model_customer

# MARKDOWN ********************

# ### Create schema and tables for product domain

# CELL ********************

%run model_product

# MARKDOWN ********************

# ### Create schema and tables for sales domain 

# CELL ********************

%run model_sales

# MARKDOWN ********************

# ### Create schema and tables for finance domain

# CELL ********************

%run model_finance

# MARKDOWN ********************

# ### Create schema and tables for inventory domain

# CELL ********************

%run model_inventory

# MARKDOWN ********************

# ### Create schema and tables for supplychain domain

# CELL ********************

%run model_supplychain

# CELL ********************

print("🎉 All schemas and tables created successfully!")
