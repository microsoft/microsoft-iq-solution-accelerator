# Fabric notebook source


# MARKDOWN ********************

# # Truncate All Tables
# 
# ## Overview
# This notebook truncates all tables across all schemas, removing data while preserving table structures.
# 
# **⚠️ WARNING**: This operation removes ALL data from ALL tables. Use only in development/testing environments.
# 
# **Schemas**: customer, product, sales, finance, inventory, supplychain

# CELL ********************

# Display warning and confirm operation
print("⚠️  WARNING: This operation will remove ALL DATA from ALL TABLES")
print("📋 Schemas to be truncated: customer, product, sales, finance, inventory, supplychain")
print("🔄 Table structures will be preserved")
print("")

# MARKDOWN ********************

# ### Truncate Customer Schema Tables

# CELL ********************

print("👥 Truncating Customer schema tables...")

# Customer schema tables
customer_tables = ['Customer', 'CustomerTradeName', 'CustomerRelationshipType', 'Location', 'CustomerAccount']

for table in customer_tables:
    try:
        spark.sql(f"TRUNCATE TABLE customer.{table}")
        print(f"   ✅ customer.{table} truncated")
    except Exception as e:
        print(f"   ❌ Error truncating customer.{table}: {str(e)}")

print("✅ Customer schema truncation complete!")

# MARKDOWN ********************

# ### Truncate Product Schema Tables

# CELL ********************

print("📦 Truncating Product schema tables...")

# Product schema tables
product_tables = ['Product', 'ProductCategory']

for table in product_tables:
    try:
        spark.sql(f"TRUNCATE TABLE product.{table}")
        print(f"   ✅ product.{table} truncated")
    except Exception as e:
        print(f"   ❌ Error truncating product.{table}: {str(e)}")

print("✅ Product schema truncation complete!")

# MARKDOWN ********************

# ### Truncate Sales Schema Tables

# CELL ********************

print("🛒 Truncating Sales schema tables...")

# Sales schema tables
sales_tables = ['Order', 'OrderLine', 'OrderPayment']

for table in sales_tables:
    try:
        spark.sql(f"TRUNCATE TABLE sales.{table}")
        print(f"   ✅ sales.{table} truncated")
    except Exception as e:
        print(f"   ❌ Error truncating sales.{table}: {str(e)}")

print("✅ Sales schema truncation complete!")

# MARKDOWN ********************

# ### Truncate Finance Schema Tables

# CELL ********************

print("💰 Truncating Finance schema tables...")

# Finance schema tables (lowercase as per schema definition)
finance_tables = ['invoice', 'account', 'payment']

for table in finance_tables:
    try:
        spark.sql(f"TRUNCATE TABLE finance.{table}")
        print(f"   ✅ finance.{table} truncated")
    except Exception as e:
        print(f"   ❌ Error truncating finance.{table}: {str(e)}")

print("✅ Finance schema truncation complete!")

# MARKDOWN ********************

# ### Truncate Inventory Schema Tables

# CELL ********************

print("📦 Truncating Inventory schema tables...")

# Inventory schema tables
inventory_tables = ['Warehouses', 'Inventory', 'InventoryTransactions', 'PurchaseOrders', 'PurchaseOrderItems', 'DemandForecast']

for table in inventory_tables:
    try:
        spark.sql(f"TRUNCATE TABLE inventory.{table}")
        print(f"   ✅ inventory.{table} truncated")
    except Exception as e:
        print(f"   ❌ Error truncating inventory.{table}: {str(e)}")

print("✅ Inventory schema truncation complete!")

# MARKDOWN ********************

# ### Truncate Supply Chain Schema Tables

# CELL ********************

print("🏭 Truncating Supply Chain schema tables...")

# Supply chain schema tables
supplychain_tables = ['Suppliers', 'ProductSuppliers', 'SupplyChainEvents']

for table in supplychain_tables:
    try:
        spark.sql(f"TRUNCATE TABLE supplychain.{table}")
        print(f"   ✅ supplychain.{table} truncated")
    except Exception as e:
        print(f"   ❌ Error truncating supplychain.{table}: {str(e)}")

print("✅ Supply Chain schema truncation complete!")

# MARKDOWN ********************

# ### Summary

# CELL ********************

print("🎉 All schema truncation operations completed!")
print("")
print("📊 Summary:")
print("   • Customer: 5 tables truncated")
print("   • Product: 2 tables truncated")
print("   • Sales: 3 tables truncated")
print("   • Finance: 3 tables truncated")
print("   • Inventory: 6 tables truncated")
print("   • Supply Chain: 3 tables truncated")
print("")
print("✅ Total: 22 tables truncated across 6 schemas")
print("🚀 Ready for fresh data loading!")
