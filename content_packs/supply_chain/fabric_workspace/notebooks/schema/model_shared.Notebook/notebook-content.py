# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# # Data Model for Shared Dimensions
# 
# ## Schema Structure
# **1 table**: DimDate
# 
# ## Data Sources
# - Generated programmatically (calendar dimension)
# 
# ## Notes
# - DateKey is INT in YYYYMMDD format (e.g., 20260402)
# - Fiscal year starts July 1
# - All fact table date columns should join to `shared.DimDate.FullDate` or `DateKey`

# CELL ********************

################################################################################################
# Schema Configuration - You can define different value here
################################################################################################

# Schema Configuration
SCHEMA_NAME = "shared"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA_NAME}")
print(f"✅ {SCHEMA_NAME} schema ready!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

################################################################################################
# Shared Dimensions - Calendar Table
################################################################################################

# 1. Create DimDate table
TABLE_NAME = "DimDate"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    DateKey INT NOT NULL,
    FullDate DATE NOT NULL,
    Year INT,
    Quarter INT,
    QuarterName STRING,
    Month INT,
    MonthName STRING,
    WeekOfYear INT,
    DayOfMonth INT,
    DayOfWeek INT,
    DayName STRING,
    IsWeekend BOOLEAN,
    IsHoliday BOOLEAN,
    FiscalYear INT,
    FiscalQuarter INT
) USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

print(f"🎉 {SCHEMA_NAME.upper()} DOMAIN COMPLETE!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
