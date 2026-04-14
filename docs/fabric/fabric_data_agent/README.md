# Fabric Data Agent

A Fabric data agent allows users to ask natural language questions against the lakehouse. There are multiple ways to create a Fabric Data Agent. We are using the Primary Approach described below. We also provide documentation on alternative methods to create a fabric data agent. 

---

## Primary Approach: Semantic Model -> Ontology -> Data Agent

Below are the key steps: 

1. Create a semantic model based on the lakehouse schema and data. 
2. Additional measurements are added. 
3. A DimDate table is added to the shared schema. 
4. Create a Fabric Ontology from the semantic model and then create a Fabric data agent using the Fabric ontology as a data source. 
5. Provide agent instructions. 

For details, please refer to files in the subfolder `data_agent_sm_ontology.` 

Please note that our deployment script will automatically create this data agent in the Fabric Workspace that the scripts create/use. 

## Alternative 1: Ontology Entity Model -> Data Agent

Below are the key steps: 

1. Create an Ontology resource.
2. Build an entity model and relationships.
3. Create a data agent using the ontology as a data source.
4. Provide data agent instructions. 

For details, please refer to files in the subfolder `data_agent_em_ontology.` Please note that our deployment script **will not create** this data agent. You can find instructions in this folder to manually create a data agent with this approach. 

## Alternative 2: Lakehouse -> Data Agent

Below are the key steps: 

1. Create a data agent with the lakehouse as the data source.
2. Provide agent instructions.
3. Provide data source instructions.
4. Provide data source descriptions.
5. Provide sample queries (optional). 

For details, please refer to files in the subfolder `data_agent_lakehouse.` Please note that our deployment script **will not create** this data agent. You can find instructions in this folder to manually create a data agent with this approach. 
