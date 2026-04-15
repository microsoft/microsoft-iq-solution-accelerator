# Fabric IQ Architecture

## Overview

The Fabric component of the Microsoft IQ Solution Accelerator implements a comprehensive data lakehouse architecture featuring semantic modeling, an ontology-based Fabric data agent with natural language querying capabilities, and interactive dashboards for retail sales and supply chain management.

## Fabric IQ Architecture

The key components of the Fabric IQ architecture are as follows

- Lakehouse with domain schema and tables 
- Pipeline that uploads source data into lakehouse schema and tables 
- Semantic models derived from lakehouse for ontology and dashboards 
- Ontology utilizes the Semantic model 
- Fabric data agent utilizes the ontology as data source 
- Sales and supply dashboards 

## Key Components 

### Data Foundation 

The solution implements a comprehensive data lakehouse with six core domain schemas. The Customer domain manages customer demographics, accounts, relationships, and geographic locations. The Product domain contains the complete product catalog with categories and product line definitions across camping, kitchen, and ski equipment. The Sales domain handles order management, line items, and payment processing for the complete order-to-cash cycle. The Finance domain manages invoicing, account management, and financial payment tracking to complete the financial workflow. 

The Inventory domain provides stock level monitoring, warehouse management, purchase order processing, and demand forecasting capabilities. The Supply Chain domain tracks supplier relationships, disruption events, and their impact analysis across the business.

### Semantic Model, Ontology, and Fabric Data Agent

The lakehouse data undergoes transformation to create a semantic model that establishes business context and relationships between entities. From this semantic model, an ontology is generated that provides the foundational knowledge structure for intelligent data interactions and natural language query processing.

A Microsoft Fabric data agent serves as the primary user interface, created directly from the ontology resource. This agent enables users to interact with the data through natural language queries, automatically translating business questions into appropriate SQL queries while maintaining full context of the business relationships and rules.

Additional information and learnings can be found in [README: semantic model ontology data agent](fabric_data_agent/data_agent_sm_ontology/README.md)

Besides the deployed fabric data agent created from above approach, two alternative approaches are documented in this repository if users choose to use them:

- Data agent based on ontology entity model: Please refer to [README: ontology entity model data agent](fabric_data_agent/data_agent_em_ontology/README.md)
- Data agent based on lakehouse: Please refer to [README: lakehouse data agent](fabric_data_agent/data_agent_lakehouse/README.md) 

### Business Intelligence Dashboards

Two specialized dashboards provide comprehensive business intelligence capabilities for sales and supply chain operations. The Sales Overview dashboard delivers insights into revenue performance, customer analytics, and business trends. The Supply Chain Management dashboard focuses on inventory optimization, supplier performance monitoring, and operational efficiency metrics.  
