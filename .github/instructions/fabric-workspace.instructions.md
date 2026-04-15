---
description: "Use when editing Fabric workspace items under fabric/fabric_workspace/. Covers Fabric Git format, item types, .platform files, parameter.yml parameterization, notebook format, and documentation sync with DeploymentGuideFabric.md."
applyTo: "fabric/fabric_workspace/**"
---

# Fabric workspace items — conventions and structure

## Fabric Git format

This folder follows the [Fabric workspace Git format](https://learn.microsoft.com/fabric/cicd/git-integration/git-get-started) for CI/CD deployment via [fabric-launcher](https://github.com/microsoft/fabric-launcher) using [Fabric's Git integration](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration).

## Item types and naming

Each item is a folder named `{name}.{Type}/` containing a `.platform` metadata file and type-specific content:

| Type suffix | Content files | Purpose |
|---|---|---|
| `.Lakehouse/` | `alm.settings.json`, `lakehouse.metadata.json`, `shortcuts.metadata.json` | Data lakehouse config |
| `.Notebook/` | `notebook-content.py` or `notebook-content.sql` | Fabric notebook |
| `.DataAgent/` | `Files/Config/data_agent.json`, `Files/Config/draft/stage_config.json` | AI data agent |
| `.Ontology/` | `definition.json` | Ontology semantic model |

### Notebook format

Python notebooks use `notebook-content.py` with comment-delimited cells:
- `# MARKDOWN ********************` — markdown cell boundary
- `# CELL ********************` — code cell boundary
- `# METADATA ********************` with `# META { ... }` — cell metadata

SQL notebooks use `notebook-content.sql` with `--` comment equivalents.

### .platform files

Every item folder contains a `.platform` JSON file with Fabric metadata (type, config schema version). These are managed by Fabric Git integration — do not manually edit GUIDs.

## Parameterization

[`parameter.yml`](../../fabric/fabric_workspace/parameter.yml) defines GUID replacements for environment-specific deployment using [fabric-cicd](https://pypi.org/project/fabric-cicd/). Notebook and DataAgent items reference lakehouse/workspace GUIDs that are substituted at deploy time.

## Current inventory

```text
fabric_workspace/
├── fabric_data_agents/           # AI Data Agents
│   ├── data_agent_lakehouse.DataAgent/   # NL query over lakehouse (22 tables, 6 domains)
│   └── data_agent_ontology.DataAgent/    # Ontology-based queries
├── fabric_ontology/
│   └── ontology_semantic_model.Ontology/ # Business-friendly semantic layer
├── lakehouses/
│   └── miqsadata.Lakehouse/     # Unified data store (shortcut-enabled)
└── notebooks/                    # 23 notebooks
    ├── data_management/ (4)      # create_scheme_tables, drop_all_tables, load_data_all_tables, truncate_all_tables
    ├── data_processing/ (6)      # load_customer, load_finance, load_inventory, load_product, load_sales, load_supplychain
    ├── query_samples/ (4)        # get_data_summary, list_schema_tables, order_counts, sql_order_counts
    ├── schema/ (6)               # model_customer, model_finance, model_inventory, model_product, model_sales, model_supplychain
    ├── pipeline_main/            # Orchestration entry-point
    ├── pipeline_update/          # Pipeline update utility
    └── reset_or_debug/           # Debug and reset utility
```

### Business domains (22 tables)

| Domain | Tables |
|---|---|
| Customer | Customer, CustomerRelationshipType, CustomerTradeName, Location, CustomerAccount |
| Product | Product, ProductCategory |
| Sales | Order, OrderLine, OrderPayment |
| Finance | invoice, account, payment |
| Inventory | Warehouses, Inventory, InventoryTransactions, PurchaseOrders, PurchaseOrderItems, DemandForecast |
| Supply chain | Suppliers, ProductSuppliers, SupplyChainEvents |

## Documentation sync

When adding, removing, or renaming items, update:

- [`docs/fabric/DeploymentGuideFabric.md`](../../docs/fabric/DeploymentGuideFabric.md) — §5 Deployment Results > Fabric Components (folder structure, item counts, notebook table, domain table)
- [`docs/fabric/DeploymentGuideFabricManual.md`](../../docs/fabric/DeploymentGuideFabricManual.md) — installer outcome list and Deployment Verification section

Also review [`.github/instructions/fabric-workspace.instructions.md`](./fabric-workspace.instructions.md) (this file) and [`.github/instructions/fabric-scripts.instructions.md`](./fabric-scripts.instructions.md) to keep the item inventory and counts current.
