# Data Agent

A Fabric data agent allows users to ask natural language questions against the lakehouse. There are multiple ways to create a Fabric Data Agent. This doc listed three of them. 

---

## Option 1: Semantic Model -> Ontology -> Data Agent

Create a semantic model based on the lakehouse schema and data. Additional measurements are added. A DimDate table is added to the shared schema. Create a Fabric Ontology from the semantic model. Create a Fabric data agent using the Fabric ontology as a data source. Provide agent instructions. For details, please refer to files in the subfolder `data_agent/data_agent_semantic_model.` 

Please note that our deployment script will automatically create this data agent in the Fabric Workspace that the scripts create/use. 

## Option 2: Ontology Entity Model -> Data Agent

Create an Ontology resource, build an entity model and relationships. Then create a data agent using the ontology as a data source. Provide data agent instructions. 

For details, please refer to files in the subfolder `data_agent/data_agent_entity_model.` 

Please note that our deployment script will not create this data agent. If you'd like to experiment with this approach, you can use the resources in the subfolder `data_agent/data_agent_entity_model` as references. 

## Option 3: Lakehouse -> Data Agent

Create a data agent with the lakehouse as the data source. Provide agent instructions, data source instructions, data source descriptions, and sample queries. 

Please note that our deployment script will not create this data agent. If you'd like to experiment with this approach, you can use the resources in the subfolder `data_agent/data_agent_lakehouse` as references. 

