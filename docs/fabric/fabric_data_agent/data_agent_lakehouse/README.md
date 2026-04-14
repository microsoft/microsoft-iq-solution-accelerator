# Lakehouse Fabric Data Agent Guide

You can manually set up a Fabric Data Agent with a lakehouse as the data source directly without using Microsoft Ontology. You can follow [Microsoft's Fabric Data Agent Guide](https://learn.microsoft.com/en-us/fabric/data-science/how-to-create-data-agent) to create or update the Fabric Data Agent, and use the materials provided here to set up your agent quickly. 

## Steps to Create a New Fabric Data Agent

1. Create a new item, search for "data agent", and you will see Fabric Data Agent.
2. Create a Fabric Data Agent with a name, for example, `data_agent_lakehouse`.
3. Add the Lakehouse named `miqsadata` (or the name of the actual data lakehouse deployed to your Fabric workspace).
4. Use the agent configuration files provided below to set up your Fabric Data Agent. You can customize them to fit your specific purposes. 

## 📁 Agent Configuration Files

This folder contains essential configuration files for setting up your Fabric Data Agent to deliver optimal intelligence based on the data loaded from this solution accelerator. 

### Core Setup Files

**[Agent Instructions - Master Prompt](agent_instructions.md)**  
Contains the primary instructions and behavior guidelines for your Fabric Data Agent. This file establishes the agent's role, scope, and response patterns.

**[Data Source Description](data_source_description.md)**  
Provides a description of the data source. 

**[Data Source Instructions](data_source_instructions.md)**  
Provides detailed information about your data structure, table relationships, and query patterns. This helps the agent understand your data and deliver more accurate, efficient responses.

**Example Questions and Query Patterns**

You can provide example questions and corresponding SQL query code. See the following files for reference:

- [Query Examples](query_examples.md) - Contains sample queries and patterns
- [Sample Agent Questions](sample_agent_questions.md) - Example questions to test your data agent

### Testing the Data Agent

Once the Data Agent is set up with the above agent configuration files, you will be able to chat with the agent immediately. You can also publish your data agent for others to use. For more sample test questions, see [sample_agent_questions.md](sample_agent_questions.md). 

## 💡 Customization Tips

- Replace sample data references with your organization's actual data structure
- Add domain-specific terminology and business context to the master instructions
- Include your most common business questions in the training examples
- Update query patterns to match your specific analytics needs
