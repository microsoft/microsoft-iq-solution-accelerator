# Instructions - Initial Setup 

1. Create a fabric workspace 
   
2. In the fabric workspace, create a lakehouse with the name of your choice. For example **miqdata** 

3. Upload the infra/data folder to the File section of the lakehouse: 

   You will have something like this: Files/data/camping, customer, inventory, kitchen, product, ski, supplychain. 

4. Create a folder named 'notebooks' in your Fabric Workspace. 

5. Upload all the files in this repo under src/fabric/notebooks to the notebooks folder in your Fabric Workspace 

6. Open the notebook named `main_pipeline.ipynb`. Add the lakehouse you created to this notebook. Then run this notebook. You will get the following results 

   - All schemas and tables created in the lakehouse 
   - All data in the Files/data folder will be loaded to the appropriate tables in the lakehouse **miqdata** 
   - You can now review the schema, tables, and data. 

## Instructions - Update Resources 

If you have regenerated data, please delete the  Files/data folder or rename it to something like Files/data_backup. And then update the new data generated (upload folder) to Files

If you have updated the fabric notebooks, please delete all older notebooks and import updated ones from your local folder

The easiest way to re-load to recreate schema and reload the data. 

Open the notebook named `update_pipeline.ipynb`. And run each cell from top to down. 
