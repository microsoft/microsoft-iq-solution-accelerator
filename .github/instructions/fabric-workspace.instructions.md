---
description: "Use when editing Fabric workspace items under fabric/fabric_workspace/. Covers Fabric Git format, item types, .platform files, parameter.yml parameterization, notebook format, and documentation sync with docs/DeploymentGuide.md and docs/fabric/DeploymentGuideFabricManual.md."
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

[`parameter.yml`](../../src/fabric/fabric_workspace/parameter.yml) defines GUID replacements for environment-specific deployment using [fabric-cicd](https://pypi.org/project/fabric-cicd/). Notebook and DataAgent items reference lakehouse/workspace GUIDs that are substituted at deploy time.

## Current inventory

```text
fabric_workspace/
├── data_agent/                    # AI Data Agent(s)
│   └── RetailSC Ontology Agent.DataAgent/   # NL queries via ontology semantic model
├── ontology/
│   └── RetailSupplyChainOntologyModel.Ontology/ # Business-friendly semantic layer
├── lakehouses/
│   └── miqsadata.Lakehouse/      # Unified data store (shortcut-enabled, 25 tables)
├── dashboards/                    # Semantic models + Power BI reports
│                                  # (RetailSupplyChainModel, Sales Overview, Supply Chain Management)
└── notebooks/                     # 26 notebooks
    ├── data_management/ (4)       # create_scheme_tables, drop_all_tables, load_data_all_tables, truncate_all_tables
    ├── data_processing/ (7)       # load_customer, load_finance, load_inventory, load_product, load_sales, load_supplychain, load_shared
    ├── query_samples/ (4)         # get_data_summary, list_schema_tables, order_counts, sql_order_counts
    ├── schema/ (7)                # model_customer, model_finance, model_inventory, model_product, model_sales, model_supplychain, model_shared
    └── (root) (4)                 # pipeline_main, pipeline_update, reset_or_debug, sample_data_query
```

> The folder names above (`data_agent/`, `ontology/`, `dashboards/`, `lakehouses/`, `notebooks/`) reflect the post-installer layout produced by `fabric_solution_installer.ipynb`. The on-disk Fabric Git format under `src/fabric/fabric_workspace/` may use flatter naming — always reconcile against the live folder structure when items are added or moved.

### Business domains (25 tables)

| Domain | Tables |
|---|---|
| Customer (5) | `Customer`, `CustomerTradeName`, `CustomerRelationshipType`, `Location`, `CustomerAccount` |
| Product (3) | `ProductLine`, `Product`, `ProductCategory` |
| Sales (3) | `Order`, `OrderLine`, `OrderPayment` |
| Finance (3) | `invoice`, `account`, `payment` |
| Inventory (6) | `Warehouses`, `Inventory`, `InventoryTransactions`, `PurchaseOrders`, `PurchaseOrderItems`, `DemandForecast` |
| Supply chain (4) | `Suppliers`, `ProductSuppliers`, `SupplyChainEvents`, `SupplyChainEventImpacts` |
| Shared (1) | `DimDate` |

## Documentation sync

When adding, removing, or renaming items, update:

- [`docs/DeploymentGuide.md`](../../docs/DeploymentGuide.md) — §7 Deployment Results → *Fabric IQ Components* (workspace tree must match the live items)
- [`docs/fabric/DeploymentGuideFabricManual.md`](../../docs/fabric/DeploymentGuideFabricManual.md) — *Verification* section (lakehouse table breakdown, notebook counts)

Also review [`.github/instructions/fabric-workspace.instructions.md`](./fabric-workspace.instructions.md) (this file) and [`.github/instructions/infra-scripts.instructions.md`](./infra-scripts.instructions.md) to keep the item inventory and counts current.
