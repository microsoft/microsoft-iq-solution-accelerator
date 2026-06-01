# Fabric Setup and Pipeline Run Guide (Manual)

This guide walks through the full process of setting up a Fabric workspace, running data pipelines, and validating results.

This step has been automated. This document provides a way that the user can manually set up the Fabric Workspace, upload data, and run the pipelines to create schema and populate all the tables in the fabric lakehouse. 

## Prerequisites

- Microsoft Fabric access with permission to create a workspace, lakehouse, and notebooks
- Git installed on your machine
- This repository available locally

## Step 1. Create Fabric workspace and lakehouse

1. Create a new Fabric workspace.
2. In that workspace, create a Lakehouse. Example name: `miqdata`.
3. Open the lakehouse and make sure you can see the `Files` section.

## Step 2. Upload the `data` subfolder to the lakehouse

1. From this repo, locate `infra/fabric/data`.
2. In Fabric Lakehouse, go to `Files`.
3. Upload the full `data` folder (not individual files one by one).

After upload, your lakehouse path should look like:

- `Files/data/customer`
- `Files/data/finance/<product_line>s` (for example `Files/data/finance/camping` or `Files/data/finance/kitchen`)
- `Files/data/inventory`
- `Files/data/product`
- `Files/data/sales/<product_line>s` (for example `Files/data/sales/camping` or `Files/data/sales/kitchen`)
- `Files/data/supplychain`

**Important**: Data loading notebooks use paths like `Files/data/customer`, `Files/data/product`. If folder names change, load steps will fail. The way to correct the problem is to synchronize the code and file structure under the `data` folder.

## Step 3. Upload notebooks to Fabric

1. In your Fabric workspace, create a folder named `notebooks`, and create subfolders under the notebooks:

   - `data_management`
   - `data_processing`
   - `query_samples`
   - `schema`

2. Upload all notebooks from `src/fabric/notebooks`, such as 

   `pipeline_main.ipynb`

   `pipeline_update.ipynb`

   `reset_or_debug.ipynb`

   `sample_data_query.ipynb`

3. Then upload notebook files from subfolders as well:
   - `data_management`
   - `data_processing`
   - `query_samples`
   - `schema`

## Step 4. Attach lakehouse and run the main pipeline

For first-time data loading, follow these steps:

1. Open `pipeline_main.ipynb` in Fabric.
2. Attach the lakehouse you created (for example `miqdata`) to the notebook session.
3. Run the notebook top-to-bottom.

If you need to update a portion of the schema, data, or data loading code, you can use the following programs:

1. `pipeline_update.ipynb`: designed to re-load entire data after code or data updates
2. `reset_or_debug.ipynb`: designed to reset or debug tables associated with one particular schema. 

## Step 5. Expected output and validation

During a successful run of `pipeline_main`, you will get a lot of messages. The last step is loading all the data to Fabric Lakehouse. You will be getting something similar to below: 

```text
✅Loading 'customer' schema from: Files/data/customer
📊Customer schema: 5 tables, 2,734 records loaded
   - Customer: 513 records
   - CustomerAccount: 1,539 records
   - CustomerRelationshipType: 9 records
   - CustomerTradeName: 160 records
   - Location: 513 records
✅Loading 'product' schema from: Files/data/product
📊Product schema: 3 tables, 93 records loaded
   - ProductLine: 3 records
   - Product: 60 records
   - ProductCategory: 30 records
✅Loading 'sales' schema from 3 product lines: camping, kitchen, ski
📊Sales schema: 3 tables, 93,084 records loaded
✅Loading 'finance' schema from 3 product lines: camping, kitchen, ski
📊Finance schema: 3 tables, 40,657 records loaded
✅Loading 'inventory' schema from: Files/data/inventory
📊Inventory schema: 6 tables, 5,521 records loaded
   - Warehouses: 3 records
   - Inventory: 83 records
   - InventoryTransactions: 4,545 records
   - PurchaseOrders: 119 records
   - PurchaseOrderItems: 351 records
   - ForecastDemand: 420 records
✅Loading 'supplychain' schema from: Files/data/supplychain
📊Supplychain schema: 4 tables, 117 records loaded
   - Suppliers: 5 records
   - ProductSuppliers: 75 records
   - SupplyChainEvents: 15 records
   - SupplyChainEventImpacts: 22 records
✅Loading 'shared' schema
DimDate populated: 3,201 rows (2018-01-01 to 2026-10-06)
📊Shared schema: 1 table, 3,201 records loaded
   - DimDate: 3,201 records (includes 6 months future for forecasting)
======================================================================
📊 DATA LOADING COMPLETE - COMPREHENSIVE SUMMARY
======================================================================
🕐 Completed at: 2026-04-06 19:46:14
======================================================================
```
