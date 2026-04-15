# Microsoft Fabric Ontology Learning Guide
## For Solution Deployers and Data Teams

---

This guide is meant to help you think clearly about ontology design in Fabric. It is not a setup checklist and it is not a product tutorial. The goal is to explain the design choices that make an ontology usable by a Data Agent, and to show the mistakes that usually make it fragile.

The simplest way to read it is this:

1. Start with the mental model.
2. Read the design guidance.
3. Use the failure patterns to review your own model.
4. Run the validation questions at the end.

## The Mental Model

```text
Prepare Data -> Create Semantic Model -> Generate Ontology -> Configure Data Agent

Prepare Data:
- Load source files into Lakehouse tables
- Validate PK and FK integrity
- Resolve data type mismatches

Create Semantic Model:
- Select tables and define relationships
- Add required measures (especially for low-numeric dimensions)
- Choose DirectLake or Import mode

Generate Ontology:
- Create entities and properties from the model
- Confirm keys, display names, and relation directions
- Bind static data first, then time-series where needed

Configure Data Agent:
- Add ontology as data source
- Add concise instructions for ambiguity and output shape
- Test with natural language queries
```


What usually goes wrong is that teams treat ontology generation as a table-conversion exercise. That produces a technically correct structure that is hard for people, and therefore hard for the agent, to use. A better ontology starts with the questions users ask and works backward into entities, properties, and relationships.

## Start With Business Concepts, Not Tables

If a user asks, "Which suppliers were affected by weather disruptions?" the business concepts are Supplier, SupplyChainEvent, and EventImpact. That is the shape of the ontology. The underlying tables matter, but they are not the design center.

In practice, it helps to classify source tables before modeling:

| Type | Role | Examples |
|------|------|----------|
| Dimension | Descriptive context | Product, Supplier, Warehouse |
| Fact | Measurable events | Inventory, PurchaseOrders, DemandForecast |
| Bridge | Many-to-many connector | ProductSuppliers |
| Shared Dimension | Reusable time context | DimDate |

The useful question is not, "Do I have an entity for every table?" The useful question is, "Can a business user ask a natural-language question and get back an answer that follows the domain model they already understand?"

## Design Keys and Relationships Conservatively

Most ontology problems are not caused by missing features. They are caused by over-modeling, ambiguous naming, or unstable keys.

For entity keys, keep the rules strict:

1. Use a single STRING or INTEGER key.
2. Do not use nulls in key columns.
3. Prefer stable business identifiers over generated values.

Composite keys tend to make ontology behavior harder to reason about. They also make downstream troubleshooting harder. If you can avoid them, avoid them.

Relationships should be designed so a human can read them without knowing the physical model. Names such as supplies, stored in, ordered from, and affected by are much more useful than generic link semantics. Relationship direction matters as well. If the model creates loops that do not add real business value, remove them.

Property naming also needs more discipline than most teams expect. In Fabric ontology generation, property names are effectively global. Reusing a name like Priority or Status with different meanings or data types across entities is an easy way to create type conflicts and subtle confusion. Names such as WarehousePriority and OrderPriority are safer because they keep meaning attached to the property.

## Prepare the Data Before You Generate the Ontology

Ontology quality is constrained by data quality. If the source model is inconsistent, the ontology will reflect that inconsistency.

The baseline requirements are straightforward:

- [ ] Managed Lakehouse tables are used (not shortcuts or external only).
- [ ] OneLake security is not enabled on the Lakehouse used for ontology generation.
- [ ] Column mapping is not enabled.
- [ ] Each table has a clear primary key column.
- [ ] Foreign keys are valid with no orphan references.
- [ ] Same-name columns across tables use compatible data types.

There are also a few decisions that are not strictly required but usually improve the result:

- [ ] Star schema separation for facts and dimensions.
- [ ] DimDate available for time intelligence.
- [ ] Descriptive names denormalized in high-use facts where practical.
- [ ] Key columns without nulls.
- [ ] Stable semantic typing for repeated concepts.

Two small optimizations are worth calling out. First, display-friendly names such as WarehouseName make the ontology far easier to browse and far easier for the agent to return in answers. Second, dimension tables with no numeric behavior may need a measure in the semantic model so they are not ignored during generation.

## Where Teams Usually Get Burned

The same failure patterns show up repeatedly.

### A table disappears from the ontology

This often happens because the table has no measurable behavior and gets skipped. The usual fix is to add a simple measure in the semantic model, such as a row count, and regenerate.

### A type conflict appears unexpectedly

This usually means the same property name was reused with a different type in another entity. The fix is not to work around the error. The fix is to rename the property so its meaning is explicit and stable everywhere.

### The Data Agent answers ID-based questions but struggles with names

This usually means the ontology can technically traverse the model, but the data agent lacks enough readable context. You can solve this in two ways: improve instructions for join and matching behavior, or denormalize a small number of high-value name columns into key fact tables.

### DirectLake works for simple queries but not multi-hop business questions

This usually points to missing or weak relationship definitions in the semantic model. DirectLake will not rescue an under-specified model. If the join path matters, define it explicitly.

## Keep Data Agent Instructions Lean

Instructions should not restate the whole ontology. They should only help where the model alone is not enough.

In most cases, the instructions need to do four things:

1. Permit aggregation behavior such as GROUP BY.
2. Define what to do when user wording does not exactly match stored values.
3. Clarify business meanings for a few metrics.
4. Require readable output fields in responses.

That is usually enough. When instructions grow too long, they start competing with the model instead of supporting it.

This pattern is often sufficient:

```text
Support GROUP BY in GQL.

When no results are found, retry with:
- Singular and plural variants
- LIKE or CONTAINS partial matching
- Related category fallback when product name misses

Always include human-readable names such as ProductName, SupplierName, and WarehouseName.

For quantity on hand or stock level, use CurrentStock.
For available stock, calculate CurrentStock - ReservedStock.
Treat negative quantities as valid for Sale, Transfer, and Damage.
```

## How to Tell Whether the Ontology Is Working

The best test is not whether generation succeeds. The best test is whether natural-language questions behave the way a business user expects.

Use a mix of simple and multi-hop questions:

| Level | Question | What It Validates |
|------|------|------|
# Microsoft Fabric Ontology Learning Guide
## For Solution Deployers and Data Teams

---

## How to Use This Guide

This is a learning document, not a setup runbook. Use it to understand design decisions,
avoid common failure patterns, and validate ontology behavior for Fabric Data Agent scenarios.

Recommended usage:

1. Read each module in order.
2. Compare the guidance with your own ontology design.
3. Run the lab queries and verify expected behavior.

Estimated time: 45 to 60 minutes.

---

## Learning Outcomes

By the end of this guide, you should be able to:

1. Model ontology entities from business concepts, not just source tables.
2. Design keys, properties, and relationships that avoid type and dependency issues.
3. Prepare data so ontology generation is stable and complete.
4. Write minimal but effective Data Agent instructions.
5. Validate ontology quality using progressive test queries.

---

## End-to-End Mental Model

```text
Prepare Data -> Create Semantic Model -> Generate Ontology -> Configure Data Agent

Prepare Data:
- Load source files into Lakehouse tables
- Validate PK and FK integrity
- Resolve data type mismatches

Create Semantic Model:
- Select tables and define relationships
- Add required measures (especially for low-numeric dimensions)
- Choose DirectLake or Import mode

Generate Ontology:
- Create entities and properties from the model
- Confirm keys, display names, and relation directions
- Bind static data first, then time-series where needed

Configure Data Agent:
- Add ontology as data source
- Add concise instructions for ambiguity and output shape
- Test with natural language queries
```

---

## Module 1: Model for Business Concepts

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

## Module 2: Keys, Relationships, and Property Naming

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

## Module 3: Data Readiness Checklist

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

## Module 4: Common Pitfalls and Recovery Patterns

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

## Module 5: Writing Lean Data Agent Instructions

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

## Module 6: Validation Lab

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
