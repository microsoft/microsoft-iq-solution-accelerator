# Fabric notebook source


# MARKDOWN ********************

# # Data Model for Customer and Product Dimentions. 
# 
# ## Schema Structure
# - **Customer Management (5 tables)**: 
# - Customer, Samples Ready: Customer_Samples.csv 
# - CustomerRelationshipType, Samples Ready: CustomerRelationshipType_samples.csv
# - CustomerTradeName, Samples Ready: CustomerTradeNames_Samples.csv
# - Location, Samples Ready: Location_Samples.csv
# - CustomerAccount, Samples Ready: CustomerAccount_Samples.csv


# MARKDOWN ********************


# CELL ********************

################################################################################################
# Schema Configuration - You can define different value here
################################################################################################

# Schema Configuration
SCHEMA_NAME = "customer"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA_NAME}")
print(f"✅ {SCHEMA_NAME} schema ready!")

# CELL ********************


################################################################################################
# Customer Domain - Customer with Contact Info, Customer Accounts, Locations, etc. 5 Tables
################################################################################################

# 1. Create Customer table  
TABLE_NAME = "Customer"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    CustomerID STRING,
    CustomerTypeID STRING, --Individual, Business, Government
    CustomerRelationshipTypeID STRING,
    DateOfBirth DATE,
    CustomerEstablishedDate DATE,
    IsActive BOOLEAN,
    FirstName STRING,
    LastName STRING,
    Gender STRING,
    PrimaryPhone STRING,
    SecondaryPhone STRING,
    PrimaryEmail STRING,
    SecondaryEmail STRING,
    CreatedBy STRING
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")


# 2. Create CustomerTradeName table
TABLE_NAME = "CustomerTradeName"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    CustomerID STRING,
    CustomerTypeID STRING, --Individual, Business, Government
    TradeNameID STRING,   
    TradeName STRING,
    PeriodStartDate DATE,
    PeriodEndDate DATE,
    CustomerTradeNameNote STRING
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")


# 3. Create CustomerRelationshipType table
TABLE_NAME = "CustomerRelationshipType"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    CustomerRelationshipTypeID STRING,  -- Individual: Standard, Premium, VIP. Business: SMB, Premier, Partner. Government: Federal, State, Local.
    CustomerRelationshipTypeName STRING,
    CustomerRelationshipTypeDescription STRING
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")


# 4. Create Location table
TABLE_NAME = "Location"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    LocationID STRING,
    CustomerID STRING,
    LocationName STRING,
    IsActive BOOLEAN,
    AddressLine1 STRING,  -- "1000 Main St" 
    AddressLine2 STRING,  -- "Apt 5" or "Suite 200"
    City STRING,
    StateID STRING,
    ZipCode STRING,
    CountryID STRING,
    SubdivisionName STRING,
    Region STRING,        -- "Northeast", "West Coast", "Midwest"
    Latitude DOUBLE,
    Longitude DOUBLE,
    Note STRING
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

# 5. Create CustomerAccount table
TABLE_NAME = "CustomerAccount"
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME} (
    CustomerAccountID STRING,
    ParentAccountID STRING,
    CustomerAccountName STRING,
    CustomerID STRING,
    IsoCurrencyCode STRING
)
USING DELTA
"""
spark.sql(create_table_sql)
print(f"✅ {SCHEMA_NAME}.{TABLE_NAME} table created!")

# CELL ********************

print(f"🎉 {SCHEMA_NAME.upper()} DOMAIN COMPLETE!")
