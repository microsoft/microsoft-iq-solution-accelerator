# Fabric Setup and Pipeline Run Guide

This guide walks through the full process of setting up Fabric workspace,  running data pipeline,  and validating results.

## Prerequisites

- Microsoft Fabric access with permission to create a workspace, lakehouse, and notebooks
- Git installed on your machine
- This repository available locally

## Step 1. Create Fabric workspace and lakehouse

1. Create a new Fabric workspace.
2. In that workspace, create a Lakehouse. Example name: `miqdata`.
3. Open the lakehouse and make sure you can see the `Files` section.

## Step 2. Upload the `data` subfolder to the lakehouse

1. From this repo, locate `fabric/infra/data`.
2. In Fabric Lakehouse, go to `Files`.
3. Upload the full `data` folder (not individual files one by one).

After upload, your lakehouse path should look like:

- `Files/data/customer`
- `Files/data/finance/<product_line>s` (for example `Files/data/finance/camping` or `Files/data/finance/kitchen`)
- `Files/data/inventory`
- `Files/data/product`
- `Files/data/sales/<product_line>s` (for example `Files/data/sales/camping` or `Files/data/sales/kitchen`)
- `Files/data/supplychain`

**Important**: data loading notebooks use paths like `Files/data/customer`, `Files/data/product`.  If folder names change, load steps will fail. The way to correct the problem is to synchronize the code and file structure under `data` folder. 

## Step 3. Upload notebooks to Fabric

1. In your Fabric workspace, create a folder named `notebooks`, and create subfolders under the notebooks:

   - `data_management`
   - `data_processing`
   - `query_samples`
   - `schema`

2. Upload all notebooks from `fabric/src/fabric/notebooks`, such as 

   `main_pipeline.ipynb`

   `update_pipeline.ipynb`

3. Then upload notebook files from subfolders as well:
   - `data_management`
   - `data_processing`
   - `query_samples`
   - `schema`

## Step 4. Attach lakehouse and run the main pipeline

1. Open `main_pipeline.ipynb` in Fabric.
2. Attach the lakehouse you created (for example `miqdata`) to the notebook session.
3. Run the notebook top-to-bottom.

If you made changes to the notebooks or data, you can review and execute `update_pipeline.ipynb` 

1. Optional cleanup (commented by default):
   - `#%run truncate_all_tables`
   - `#%run drop_all_tables`
2. Schema and table creation:
   - `%run create_scheme_tables`
3. Data load into all tables:
   - `%run load_data_all_tables`

## Step 5. Expected output and validation

During a successful run of `main_pipeline`, you should see messages similar to:

```text
🎉 All schemas and tables created successfully!

✅ Loading 'customer' schema from: Files/data/customer
✅ Customer schema: 5 tables, 2,734 records loaded
✅ Loading 'product' schema from: Files/data/product
✅ Product schema: 2 tables, 90 records loaded
✅ Loading 'sales' schema from 3 product lines: camping, kitchen, ski
✅ Sales schema: 3 tables, 90,192 records loaded
✅ Loading 'finance' schema from 3 product lines: camping, kitchen, ski
✅ Finance schema: 3 tables, 39,557 records loaded
✅ Loading 'inventory' schema from: Files/data/inventory
✅ Inventory schema: 6 tables, 5,500 records loaded
✅ Loading 'supplychain' schema from: Files/data/supplychain
✅ Supplychain schema: 3 tables, 93 records loaded
✅ Data loading is complete at: [2026-03-19 18:32:47] 
```

Final expected state:

- 6 schemas created: `customer`, `product`, `sales`, `finance`, `inventory`, `supplychain`
- 22 total tables created and populated
- Data loaded from `Files/data/...` into corresponding lakehouse tables

## Common issues

- `Path not found` errors: confirm `Files/data/...` folder structure matches exactly.
- Notebook reference errors on `%run`: verify all required notebooks were uploaded.
- Table already exists or duplicate-data scenarios: use the optional cleanup cells and rerun.