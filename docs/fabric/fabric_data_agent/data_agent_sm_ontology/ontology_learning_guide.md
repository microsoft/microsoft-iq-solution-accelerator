# Microsoft Fabric Ontology Learning Guide
## For Solution Deployers and Data Teams

> ⚠️ **Preview:** Fabric Ontology is currently a preview feature. Auto-generation from a semantic model may not fully bind all entity properties or create all relationships. Expect to manually verify and complete data bindings and relationship definitions.

---

## How to Use This Guide

This is a learning document, not a setup runbook. Use it to understand what an ontology is, how to design one well, avoid common failure patterns, and validate ontology behavior for Fabric Data Agent scenarios.

1. Read each module in order.
2. Compare the guidance with your own ontology design.
3. Run the lab queries and verify expected behavior.

---

## Learning Outcomes

By the end of this guide, you should be able to:

1. Explain what a Fabric Ontology is and how it connects to data agents.
2. Model ontology entities from business concepts, not just source tables.
3. Design keys, properties, and relationships that avoid type and dependency issues.
4. Prepare data so ontology generation is stable and complete.
5. Write minimal but effective Data Agent instructions.
6. Validate ontology quality using progressive test queries.

---

## Module 1: What Is a Fabric Ontology?

A [Fabric Ontology](https://learn.microsoft.com/fabric/iq/ontology/ontology-overview) is a semantic layer that defines:

- **Entity types** — business concepts (e.g., Product, Supplier, Warehouse)
- **Properties** — attributes of each entity (e.g., ProductName, ListPrice)
- **Relationship types** — how entities connect (e.g., Product *supplied by* Supplier)

When used as a data source for a Fabric Data Agent, the ontology lets the agent translate natural language into structured [GQL](https://learn.microsoft.com/fabric/iq/ontology/gql-overview) queries.

### How It Fits in the Architecture

```
Lakehouse (Delta) ──> Semantic Model (Relationships + Measures) ──> Ontology (Entities + Rels) ──> Data Agent (NL → GQL)
```

| Component | Role |
|---|---|
| **Lakehouse** | Raw data storage (Delta tables) |
| **Semantic Model** | Adds relationships, measures, and business naming |
| **Ontology** | Entity graph generated from the semantic model |
| **Data Agent** | Answers natural language questions using the ontology |

### How the Data Agent Uses the Ontology

1. User asks: *"Which products are supplied by Contoso?"*
2. Agent identifies entities: `Product`, `Supplier`, `ProductSuppliers`
3. Agent finds relationship path: `Supplier → ProductSuppliers → Product`
4. Agent generates GQL query and executes it
5. Agent returns human-readable results

The ontology provides the **map** — the agent follows the paths.

### Ontology vs. Direct Lakehouse

| Aspect | With Ontology | Without (Direct Lakehouse) |
|---|---|---|
| Query language | GQL (graph-based) | T-SQL |
| Relationships | Explicitly modeled | Agent must infer joins |
| Measures | Available from semantic model | Not available |
| Accuracy | Higher — structured paths | Lower — ambiguous joins |
| Setup time | More steps | Minimal |

---

## Module 2: Model for Business Concepts

If a user asks, "Which suppliers were affected by weather disruptions?" the business concepts are Supplier, SupplyChainEvent, and EventImpact. That is the shape of the ontology. The underlying tables matter, but they are not the design center.

In practice, it helps to classify source tables before modeling:

| Type | Role | Examples |
|------|------|----------|
| Dimension | Descriptive context | Product, Supplier, Warehouse |
| Fact | Measurable events | Inventory, PurchaseOrders, DemandForecast |
| Bridge | Many-to-many connector | ProductSuppliers |
| Shared Dimension | Reusable time context | DimDate |

The useful question is not, "Do I have an entity for every table?" The useful question is, "Can a business user ask a natural-language question and get back an answer that follows the domain model they already understand?"

---

## Module 3: Model for Business Concepts

### Principle

Do not mirror table count to entity count. Start from user intent.

Better question:

1. What business questions should users ask?
2. Which concepts are central to those questions?
3. Which relationships are required to answer those questions?

### Classify Tables Before Modeling

| Type | Role | Examples |
|------|------|----------|
| Dimension | Descriptive context | Product, Supplier, Warehouse |
| Fact | Measurable events | Inventory, PurchaseOrders, DemandForecast |
| Bridge | Many-to-many connector | ProductSuppliers |
| Shared Dimension | Reusable time context | DimDate |

### What Good Looks Like

1. You can explain each entity in business terms, not table terms.
2. Bridge tables only exist to connect concepts and are not treated as business facts.
3. Time-based questions clearly route through DimDate or an equivalent date structure.

### Apply It

1. Pick three user questions your team cares about.
2. List which entities and relationships are needed to answer each one.
3. Remove any entity that exists only because a source table exists, but adds no user-facing value.

---

## Module 4: Keys, Relationships, and Property Naming

### Entity Key Rules

Use these rules consistently:

1. One key column only, using STRING or INTEGER.
2. No null key values.
3. Key values must be stable over time.

Avoid:

1. Composite keys.
2. Auto-generated opaque identifiers when business IDs exist.

### Relationship Design Rules

1. Use active verb semantics such as supplies, stored in, ordered from.
2. Make relationship direction explicit and meaningful.
3. Avoid circular links unless truly required.
4. For many-to-many patterns, connect bridge tables on both sides.

### Property Naming Rules

Use globally unambiguous names.

Examples:

1. Use CurrentStock, not cs.
2. Use WarehousePriority and OrderPriority instead of reusing Priority.

Critical note:
Property names are treated globally in ontology generation. Reusing the same name with different
types in different entities can cause type conflict failures.

### What Good Looks Like

1. Every entity has one stable key.
2. Relationship names are understandable to a business reader.
3. No property name is reused with conflicting meaning or type.
4. Relationship paths are useful without creating loops.

### Apply It

1. Scan your model for repeated property names such as Status, Priority, or Type.
2. Rename any property whose meaning changes across entities.
3. Draw the shortest path between Product, Supplier, Warehouse, and Forecast data. If a shortcut creates a loop, remove it.

---

## Module 5: Data Readiness Checklist

### Must Have

- [ ] Managed Lakehouse tables are used (not shortcuts or external only).
- [ ] OneLake security is not enabled on the Lakehouse used for ontology generation.
- [ ] Column mapping is not enabled.
- [ ] Each table has a clear primary key column.
- [ ] Foreign keys are valid with no orphan references.
- [ ] Same-name columns across tables use compatible data types.

### Should Have

- [ ] Star schema separation for facts and dimensions.
- [ ] DimDate available for time intelligence.
- [ ] Descriptive names denormalized in high-use facts where practical.
- [ ] Key columns without nulls.
- [ ] Stable semantic typing for repeated concepts.

### Nice to Have

- [ ] Display-friendly instance names such as WarehouseName.
- [ ] At least one measure for dimension tables with no numeric columns.

### What Good Looks Like

1. Fact-to-dimension joins resolve cleanly with no orphan keys.
2. Repeated business concepts use the same data type everywhere.
3. High-value facts expose enough descriptive context for readable answers.

### Apply It

1. Validate one fact table end to end against each related dimension.
2. Check that every foreign key has a matching primary key.
3. For one important fact table, decide whether adding ProductName or SupplierName would reduce multi-hop query complexity.

---

## Module 6: Common Pitfalls and Recovery Patterns

### Pitfall 1: Table Missing in Ontology

Cause: Table has no measurable numeric behavior and gets skipped.

Recovery:

1. Add a measure in the semantic model, for example COUNTROWS on the table.
2. Regenerate ontology metadata.

### Pitfall 2: Type Conflict Error

Cause: Same property name appears with different types across entities.

Recovery:

1. Rename properties to globally unique names by business meaning.
2. Keep one stable type per concept.

### Pitfall 3: Agent Cannot Resolve Name-Based Questions

Cause: Facts contain IDs but no readable names and instructions are too thin.

Recovery:

1. Add join-path instruction hints.
2. Optionally denormalize name columns into key facts.

### Pitfall 4: DirectLake Relationship Gaps

Cause: Relationships were assumed, not explicitly defined.

Recovery:

1. Define all required relationships in the semantic model manually.
2. Revalidate join paths with medium and advanced test questions.

### Red Flags

1. A table disappears from ontology generation after a model change.
2. A property starts failing because its type changed in another entity.
3. The Data Agent can answer ID-based queries but not name-based ones.
4. DirectLake works for simple queries but fails on joined business questions.

### Apply It

1. Pick one past failure from your project.
2. Classify it as schema, relationship, naming, or instruction quality.
3. Write the smallest change that would have prevented it.

---

## Module 7: Writing Lean Data Agent Instructions

Good instructions are short, specific, and focused on ambiguity handling and response shape.

Use this minimal pattern:

```text
Support GROUP BY in GQL.

When no results are found, retry with:
- Singular and plural variants
- LIKE or CONTAINS partial matching
- Related category fallback when product name misses

Always include human-readable names (ProductName, SupplierName, WarehouseName) with IDs.

For quantity on hand or stock level, use CurrentStock.
For available stock, calculate CurrentStock - ReservedStock.
Treat negative quantities as valid for Sale, Transfer, and Damage.
```

### What Good Looks Like

1. Instructions are short enough to read in under a minute.
2. They define fallback behavior, not the entire ontology.
3. They improve ambiguity handling and output quality without duplicating model logic.

### Apply It

1. Remove any instruction that merely repeats an obvious relationship already modeled.
2. Keep only the rules that change agent behavior: fallback matching, metric interpretation, and response shape.
3. Test whether shorter instructions improve consistency on three medium-complexity questions.

---

## Module 8: Validation Lab

Run these questions from easy to advanced.

| Level | Question | What It Validates |
|------|------|------|
| Beginner | How many products do we have? | Single-entity count behavior |
| Beginner | List all warehouses | Entity listing and display naming |
| Intermediate | Which products are supplied by Contoso Ltd? | Bridge traversal |
| Intermediate | What is the current stock of Alpine Explorer Tent? | Product and inventory join |
| Intermediate | Show all purchase orders that are Delivered | Filter behavior on status |
| Advanced | What is the demand forecast for Tents for May 2026? | Category to product to forecast path |
| Advanced | List top 5 products by current stock in Main Distribution Center | Multi-hop join plus sort and limit |
| Advanced | Which suppliers were affected by weather disruptions? | Event impact traversal |

Lab success criteria:

1. Answers include readable names, not IDs only.
2. Aggregations include group key and metric value.
3. Sorting and limits match the question.
4. Ambiguous terms trigger clarification or robust fallback.

---

## Quick Self-Assessment

If you can answer yes to all questions below, your ontology is learning-ready and production-ready.

1. Are all key relationships explicit and non-circular?
2. Are property names globally unambiguous?
3. Can the Data Agent resolve both exact and user-friendly naming?
4. Do advanced test questions return stable, readable outputs?

---

## References

- [Bind Data to Ontology](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-bind-data)
- [Create Entity Types](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-create-entity-types)
- [Create Relationship Types](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-create-relationship-types)
- [Tutorial: Create Data Agent](https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-4-create-data-agent)
- [Fabric IQ Ontology Strategy](https://www.refactored.pro/blog/2025/12/16/fabric-iq-ontology-strategy)

---

Created for the Unified Data Foundation Solution Accelerator team - April 2026
