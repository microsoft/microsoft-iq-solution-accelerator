# Fabric notebook source


# MARKDOWN ********************

# # Drop All Tables
# 
# ## Overview
# This notebook drops all tables across all schemas, removing both data and table structures.
# 
# **⚠️ WARNING**: This operation drops ALL tables and their structures. Use only in development/testing environments.
# 
# **Schemas**: customer, product, sales, finance, inventory, supplychain

# CELL ********************

# Display warning and confirm operation
print("⚠️  WARNING: This operation will PERMANENTLY DROP ALL TABLES")
print("📋 Schemas to be affected: customer, product, sales, finance, inventory, supplychain")
print("🗑️  Table structures and data will be completely removed")
print("")

# MARKDOWN ********************

# ### Drop Customer Schema Tables

# CELL ********************

print("👥 Dropping Customer schema tables...")

# Customer schema tables
customer_tables = ['Customer', 'CustomerTradeName', 'CustomerRelationshipType', 'Location', 'CustomerAccount']

for table in customer_tables:
    try:
        spark.sql(f"DROP TABLE IF EXISTS customer.{table}")
        print(f"   ✅ customer.{table} dropped")
    except Exception as e:
        print(f"   ❌ Error dropping customer.{table}: {str(e)}")

print("✅ Customer schema table drop complete!")

# MARKDOWN ********************

# ### Drop Product Schema Tables

# CELL ********************

print("📦 Dropping Product schema tables...")

# Product schema tables
product_tables = ['Product', 'ProductCategory']

for table in product_tables:
    try:
        spark.sql(f"DROP TABLE IF EXISTS product.{table}")
        print(f"   ✅ product.{table} dropped")
    except Exception as e:
        print(f"   ❌ Error dropping product.{table}: {str(e)}")

print("✅ Product schema table drop complete!")

# MARKDOWN ********************

# ### Drop Sales Schema Tables

# CELL ********************

print("🛒 Dropping Sales schema tables...")

# Sales schema tables
sales_tables = ['Order', 'OrderLine', 'OrderPayment']

for table in sales_tables:
    try:
        spark.sql(f"DROP TABLE IF EXISTS sales.{table}")
        print(f"   ✅ sales.{table} dropped")
    except Exception as e:
        print(f"   ❌ Error dropping sales.{table}: {str(e)}")

print("✅ Sales schema table drop complete!")

# MARKDOWN ********************

# ### Drop Finance Schema Tables

# CELL ********************

print("💰 Dropping Finance schema tables...")

# Finance schema tables (lowercase as per schema definition)
finance_tables = ['invoice', 'account', 'payment']

for table in finance_tables:
    try:
        spark.sql(f"DROP TABLE IF EXISTS finance.{table}")
        print(f"   ✅ finance.{table} dropped")
    except Exception as e:
        print(f"   ❌ Error dropping finance.{table}: {str(e)}")

print("✅ Finance schema table drop complete!")

# MARKDOWN ********************

# ### Drop Inventory Schema Tables

# CELL ********************

print("📦 Dropping Inventory schema tables...")

# Inventory schema tables
inventory_tables = ['Warehouses', 'Inventory', 'InventoryTransactions', 'PurchaseOrders', 'PurchaseOrderItems', 'DemandForecast']

for table in inventory_tables:
    try:
        spark.sql(f"DROP TABLE IF EXISTS inventory.{table}")
        print(f"   ✅ inventory.{table} dropped")
    except Exception as e:
        print(f"   ❌ Error dropping inventory.{table}: {str(e)}")

print("✅ Inventory schema table drop complete!")

# MARKDOWN ********************

# ### Drop Supply Chain Schema Tables

# CELL ********************

print("🏭 Dropping Supply Chain schema tables...")

# Supply chain schema tables
supplychain_tables = ['Suppliers', 'ProductSuppliers', 'SupplyChainEvents']

for table in supplychain_tables:
    try:
        spark.sql(f"DROP TABLE IF EXISTS supplychain.{table}")
        print(f"   ✅ supplychain.{table} dropped")
    except Exception as e:
        print(f"   ❌ Error dropping supplychain.{table}: {str(e)}")

print("✅ Supply Chain schema table drop complete!")

# MARKDOWN ********************

# ### Summary

# CELL ********************

print("🎉 All table drop operations completed!")
print("")
print("📊 Summary:")
print("   • Customer: 5 tables dropped")
print("   • Product: 2 tables dropped")
print("   • Sales: 3 tables dropped")
print("   • Finance: 3 tables dropped")
print("   • Inventory: 6 tables dropped")
print("   • Supply Chain: 3 tables dropped")
print("")
print("✅ Total: 22 tables dropped across 6 schemas")
print("🚀 Ready for complete fresh environment setup!")
