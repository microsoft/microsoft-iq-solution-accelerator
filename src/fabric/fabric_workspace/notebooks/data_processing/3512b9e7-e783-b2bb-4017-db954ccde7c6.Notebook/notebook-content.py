# Fabric notebook source


# MARKDOWN ********************

# # Finance Data Loading
# 
# This notebook loads all finance-related CSV files from three product line directories into Delta tables.
# 
# ## Data Sources:
# - **Camping**: Files/data/finance/camping/
# - **Kitchen**: Files/data/finance/kitchen/
# - **Ski**: Files/data/finance/ski/
# 
# ## Tables to Load:
# 1. **Invoice** - Customer invoices from all three product lines
# 2. **Account** - Financial accounts from all three product lines  
# 3. **Payment** - Customer payments from all three product lines

# CELL ********************

# Setup and Configuration
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Schema Configuration
SCHEMA_NAME = "finance"
BASE_PATH = "Files/data/finance"

# Product line paths
PRODUCT_LINES = ['camping', 'kitchen', 'ski']

# Ensure schema exists
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA_NAME}")
print(f"✅Loading '{SCHEMA_NAME}' schema from {len(PRODUCT_LINES)} product lines: {', '.join(PRODUCT_LINES)}")

# CELL ********************

# 1. Load Invoice Table from All Product Lines
invoice_dfs = []
for product_line in PRODUCT_LINES:
    df = spark.read.csv(f"{BASE_PATH}/{product_line}/Invoice_Samples_{product_line.title()}.csv", header=True, inferSchema=False)
    invoice_dfs.append(df)

combined_invoices_df = invoice_dfs[0]
for df in invoice_dfs[1:]:
    combined_invoices_df = combined_invoices_df.union(df)

combined_invoices_df = combined_invoices_df \
    .withColumn("InvoiceDate", col("InvoiceDate").cast("date")) \
    .withColumn("DueDate", col("DueDate").cast("date")) \
    .withColumn("SubTotal", col("SubTotal").cast("double")) \
    .withColumn("TaxAmount", col("TaxAmount").cast("double")) \
    .withColumn("TotalAmount", col("TotalAmount").cast("double"))
combined_invoices_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.invoice")
invoices_count = combined_invoices_df.count()

# CELL ********************

# 2. Load Account Table from All Product Lines
account_dfs = []
for product_line in PRODUCT_LINES:
    df = spark.read.csv(f"{BASE_PATH}/{product_line}/Account_Samples_{product_line.title()}.csv", header=True, inferSchema=False)
    account_dfs.append(df)

combined_accounts_df = account_dfs[0]
for df in account_dfs[1:]:
    combined_accounts_df = combined_accounts_df.union(df)

combined_accounts_df = combined_accounts_df \
    .withColumn("CreatedDate", col("CreatedDate").cast("date")) \
    .withColumn("ClosedDate", col("ClosedDate").cast("date")) \
    .withColumn("Balance", col("Balance").cast("double"))
combined_accounts_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.account")
accounts_count = combined_accounts_df.count()

# CELL ********************

# 3. Load Payment Table from All Product Lines
payment_dfs = []
for product_line in PRODUCT_LINES:
    df = spark.read.csv(f"{BASE_PATH}/{product_line}/Payment_Samples_{product_line.title()}.csv", header=True, inferSchema=False)
    payment_dfs.append(df)

combined_payments_df = payment_dfs[0]
for df in payment_dfs[1:]:
    combined_payments_df = combined_payments_df.union(df)

combined_payments_df = combined_payments_df \
    .withColumn("PaymentDate", col("PaymentDate").cast("date")) \
    .withColumn("PaymentAmount", col("PaymentAmount").cast("double"))
combined_payments_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.payment")
finance_payments_count = combined_payments_df.count()

# CELL ********************

# Summary
total_records = invoices_count + accounts_count + finance_payments_count
print(f"📊Finance schema: 3 tables, {total_records:,} records loaded")
