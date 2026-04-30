# Semantic Model Ontology — Fabric Data Agent Guide

This guide explains how to create a Microsoft Fabric Data Agent using a **Semantic Model → Ontology** approach. This is the **Primary Approach** from the [Fabric Data Agent overview](../README.md).

> **Note:** Our deployment script automatically creates this data agent. You only need this guide if you want to understand the process or recreate it manually.

---

## What Is This Approach?

Instead of pointing a data agent directly at raw lakehouse tables, this approach adds two semantic layers:

```
Lakehouse → Semantic Model → Ontology → Data Agent
```

| Layer | What It Does |
|---|---|
| **Semantic Model** | Defines table relationships, measures, and business-friendly naming on top of the lakehouse |
| **Ontology** | Auto-generates entity types, properties, and relationships from the semantic model |
| **Data Agent** | Uses the ontology to answer natural language questions via GQL |

**Why this matters:** The semantic model gives the ontology (and therefore the agent) richer context — relationships, measures, and display names — resulting in more accurate answers than pointing directly at raw tables.

---

## Prerequisites

- A Microsoft Fabric workspace with a deployed lakehouse (`miqsadata` or equivalent)
- Contributor or higher permissions on the workspace
- Lakehouse tables loaded (16 Delta tables across 4 domain schemas)
- Familiarity with [Fabric Semantic Models](https://learn.microsoft.com/fabric/get-started/direct-lake-overview)

---

## Steps to Create the Data Agent

### Step 1 — Create a Semantic Model

1. In your Fabric workspace, navigate to the lakehouse.
2. Select **New semantic model** from the lakehouse toolbar.
3. Name it, for example, `RetailSupplyChainSemanticModel`.
4. Select all tables across the 4 domain schemas.
5. Define relationships between tables (see [semantic_model_guide.md](semantic_model_guide.md) for details).
6. Add measures for dimension tables that have no numeric columns (e.g., `COUNTROWS` on `ProductCategory`).
7. Optionally add a `DimDate` table for time intelligence.

### Step 2 — Create an Ontology from the Semantic Model

> ⚠️ **Preview Feature:** Fabric Ontology is currently in **preview**. Auto-generation of entities and relationships from a semantic model is not always reliable. In most cases, you will need to manually open each entity to data-bind its properties and manually define relationships between entities. Plan for this manual step.

1. In your workspace, select **New item** → search for **Ontology**.
2. Name it, for example, `RetailSupplyChainOntologyModel`.
3. Select **Semantic Model** as the source and choose the model from Step 1.
4. Fabric attempts to auto-generate entities, properties, and relationships — **but this often requires manual intervention** (see note above).
5. **Verify data bindings:** Open each entity and confirm that its properties are correctly bound to the underlying semantic model columns. If any properties show as unbound, manually bind them.
6. **Verify relationships:** Check that relationships between entities were created. If missing, manually define them in the ontology editor using the key pairs listed in [semantic_model_guide.md](semantic_model_guide.md).
7. Review the generated entities — verify that all expected tables appear.
8. If a table is missing, add a measure to that table in the semantic model and regenerate.

### Step 3 — Create the Fabric Data Agent

1. In your workspace, select **New item** → search for **Data Agent**.
2. Name it, for example, `data_agent_ontology`.
3. Under **Data sources**, select **Ontology** and choose the ontology from Step 2.
4. Paste agent instructions from [data_agent_instructions.md](data_agent_instructions.md).
5. Save and start chatting.

---

## 📁 Agent Configuration Files

### Core Setup Files

**[semantic_model_guide.md](semantic_model_guide.md)** — Tables to include, relationships to define (with key pairs), measures to add, and DirectLake configuration for the semantic model.

**[ontology_overview.md](ontology_overview.md)** — Solution-specific ontology reference: all 16 entities across 4 domains, their relationships, join keys, and common query paths for the `RetailSupplyChainOntologyModel`.

**[data_agent_instructions.md](data_agent_instructions.md)** — Agent behavior instructions to paste into the Data Agent configuration. Covers query matching, fallback logic, metric definitions, and response formatting.

**[ontology_learning_guide.md](ontology_learning_guide.md)** — 7-module deep-dive on ontology concepts, design patterns, key rules, data readiness, common pitfalls, and validation techniques.

### Testing the Data Agent

**[sample_agent_questions.md](sample_agent_questions.md)** — 15 test questions across beginner, intermediate, and advanced levels with expected behavior and validation criteria.

---

## Key Differences from Other Approaches

| | SM → Ontology (this) | Entity Model Ontology | Lakehouse Direct |
|---|---|---|---|
| **Semantic layer** | Semantic Model + Ontology | Manual Ontology only | None |
| **Relationships** | Auto-generated from model | Manually defined | None (agent infers) |
| **Measures** | Supported | Limited | Not available |
| **Setup effort** | Medium | High | Low |
| **Query accuracy** | Highest | High | Moderate |
| **Auto-deployed** | ✅ Yes | ❌ Manual | ❌ Manual |

---

## Testing

Once set up, use the questions in [sample_agent_questions.md](sample_agent_questions.md) to validate the agent across all four domains. Start with simple queries and progress to multi-hop business questions.

---

## Customization Tips

- Add new measures in the semantic model to enable new aggregation types
- Update agent instructions when adding new entities or changing business terminology
- Regenerate the ontology after semantic model changes — it does not auto-sync
- For advanced design guidance, see the [Ontology Learning Guide](ontology_learning_guide.md)
