# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# # Shared Data Loading
# 
# This notebook populates shared dimension tables used across all schemas.
# 
# ## Tables to Load:
# 1. **DimDate** - Calendar dimension with fiscal year alignment (generated programmatically)
# 
# ## Data Sources:
# - Generated dynamically from 2018-01-01 through 6 months from today
# - Includes US federal holidays and fiscal year calculations

# CELL ********************

# Setup and Configuration
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime, timedelta
from pyspark.sql import Row
import calendar

# Schema Configuration
SCHEMA_NAME = "shared"

# Ensure schema exists
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA_NAME}")
print(f"✅Loading '{SCHEMA_NAME}' schema")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# 1. Generate and Load DimDate Table
# Dynamic date range: 2018-01-01 through 6 months from today
start_date = datetime(2018, 1, 1)
today = datetime.now()
end_month = today.month + 6
end_year = today.year + (end_month - 1) // 12
end_month = ((end_month - 1) % 12) + 1
end_date = today.replace(year=end_year, month=end_month)

# US Federal Holidays (simplified)
us_holidays = set()
for year in range(start_date.year, end_date.year + 1):
    us_holidays.add(f"{year}-01-01")  # New Year
    us_holidays.add(f"{year}-07-04")  # Independence Day
    us_holidays.add(f"{year}-12-25")  # Christmas
    us_holidays.add(f"{year}-11-11")  # Veterans Day

schema = StructType([
    StructField("DateKey", IntegerType(), False),
    StructField("FullDate", DateType(), False),
    StructField("Year", IntegerType(), True),
    StructField("Quarter", IntegerType(), True),
    StructField("QuarterName", StringType(), True),
    StructField("Month", IntegerType(), True),
    StructField("MonthName", StringType(), True),
    StructField("WeekOfYear", IntegerType(), True),
    StructField("DayOfMonth", IntegerType(), True),
    StructField("DayOfWeek", IntegerType(), True),
    StructField("DayName", StringType(), True),
    StructField("IsWeekend", BooleanType(), True),
    StructField("IsHoliday", BooleanType(), True),
    StructField("FiscalYear", IntegerType(), True),
    StructField("FiscalQuarter", IntegerType(), True),
])

rows = []
current = start_date
while current <= end_date:
    date_key = int(current.strftime("%Y%m%d"))
    fiscal_year = current.year if current.month >= 7 else current.year - 1
    fiscal_quarter = ((current.month - 7) % 12) // 3 + 1

    rows.append((
        date_key,
        current.date(),
        current.year,
        (current.month - 1) // 3 + 1,
        f"Q{(current.month - 1) // 3 + 1}",
        current.month,
        calendar.month_name[current.month],
        current.isocalendar()[1],
        current.day,
        current.isoweekday(),
        calendar.day_name[current.weekday()],
        current.weekday() >= 5,
        current.strftime("%Y-%m-%d") in us_holidays,
        fiscal_year,
        fiscal_quarter
    ))
    current += timedelta(days=1)

df = spark.createDataFrame(rows, schema=schema)

# Clear existing data and reload
spark.sql(f"TRUNCATE TABLE {SCHEMA_NAME}.DimDate")
df.write.mode("append").format("delta").saveAsTable(f"{SCHEMA_NAME}.DimDate")
dimdate_count = len(rows)

print(f"DimDate populated: {dimdate_count:,} rows ({start_date.date()} to {end_date.date()})")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Summary
total_records = dimdate_count
print(f"📊Shared schema: 1 table, {total_records:,} records loaded")
print(f"   - DimDate: {dimdate_count:,} records (includes 6 months future for forecasting)")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
