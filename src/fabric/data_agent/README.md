# Data Agent

A Fabric data agent lets users ask natural language questions against the lakehouse. Choose one of the three setup options below — you only need one that is best for your scenarios. 

---

## Option 1: Lakehouse (Direct)

Create a data agent with the lakehouse as the data source.

**Supporting files** (`data_agent_lakehouse/`):

| File | Purpose |
|------|---------|
| `data_source_description.md` | Schema catalog — all tables and fields across the 6 domains |
| `data_source_instructions.md` | Query guidance — join patterns, required filters, common pitfalls |
| `query_examples.md` | 5 verified example questions with working SQL queries |
| `agent_instructions.md` | System prompt / instructions to configure the agent |
| `sample_agent_questions.md` | Sample questions to test the agent |

---

## Option 2: Ontology + Semantic Model

Create a semantic model from the ontology, then use that semantic model as the data agent's data source.

Files: `data_agent_ontology_semantic_model/` *(in progress)*

## Option 3: Ontology Graph Model

Link the lakehouse schema and tables using an ontology graph model, then use that ontology as the data agent's data source.

Files: `data_agent_ontology_graph_model/` *(in progress)*

---

