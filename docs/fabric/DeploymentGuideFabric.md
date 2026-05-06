# Deployment Guide — Fabric IQ deep-dive

This is a **Fabric-focused companion** to the top-level [DeploymentGuide.md](../DeploymentGuide.md). It covers everything that is specific to the **Fabric IQ** half of the accelerator — the bootstrap steps that create the workspace, the items deployed inside it, the permission model, and the known limitations of the Fabric REST APIs.

> **Looking for the standard `azd up` walkthrough?** Use [`docs/DeploymentGuide.md`](../DeploymentGuide.md). It covers prerequisites, environment setup options (Local, Codespaces, Dev Container, GitHub Actions), `azd up` commands, optional configuration variables, and cleanup. This guide is for users who want to understand or extend the Fabric-specific behavior.

There are three deployment paths to choose from:

| Path | Provisions | When to use |
|---|---|---|
| **Full automated deployment** ([DeploymentGuide.md](../DeploymentGuide.md)) | Azure infrastructure (Bicep) + Fabric workspace + Foundry resources | Default; the supported end-to-end path. |
| **This guide** | Same as full deployment | When you need Fabric internals, troubleshooting, or want to extend Phase 2. |
| **Manual notebook-only deployment** ([DeploymentGuideFabricManual.md](./DeploymentGuideFabricManual.md)) | Fabric workspace items only — **no Azure infrastructure, no Foundry, no Chat Agent** | When you already have a Fabric capacity and only want the Fabric workspace contents. |

---

## Table of Contents

1. [Fabric-specific Prerequisites](#fabric-specific-prerequisites)
2. [Phase 2 — Fabric bootstrap details](#phase-2--fabric-bootstrap-details)
3. [Inside the installer notebook](#inside-the-installer-notebook)
4. [Fabric workspace contents](#fabric-workspace-contents)
5. [Workspace administrators](#workspace-administrators)
6. [Fabric capacity SKU guidance](#fabric-capacity-sku-guidance)
7. [Known limitations](#known-limitations)
8. [Additional resources](#additional-resources)

---

## Fabric-specific Prerequisites

In addition to the [Common requirements](../DeploymentGuide.md#deployment-environment-setup) listed in the main guide, the Fabric portion of the deployment requires:

### Tenant / capacity

- **Microsoft Fabric capacity** — created automatically by the deployment (default SKU `F2`), unless you bring your own via `AZURE_EXISTING_FABRIC_CAPACITY_NAME`.
- **`Microsoft.Fabric` resource provider** registered on the subscription. See [resource provider registration](https://learn.microsoft.com/azure/azure-resource-manager/management/azure-services-resource-providers).
- **Fabric tenant settings** allowing service principals to call the Fabric REST APIs (required for CI/CD and any non-interactive deployment). See [Service Principal Fabric API access](https://learn.microsoft.com/fabric/admin/metadata-scanning-enable-read-only-apis).

### API permissions for the deployment identity

| API | Permission | Purpose |
|---|---|---|
| [Fabric REST API](https://learn.microsoft.com/rest/api/fabric/) | Workspace + Item management | Create/find workspace, assign capacity, upload and run notebooks |
| [Microsoft Graph API](https://learn.microsoft.com/graph/permissions-reference#user-permissions) | `User.Read`, `openid` (delegated) | Resolve workspace administrator UPNs to object IDs |
| [Power BI REST API](https://learn.microsoft.com/rest/api/power-bi/) | `Tenant.Read.All` (delegated) | Read tenant info during workspace setup |

For service-principal deployments (CI/CD with OIDC), use object IDs instead of UPNs to avoid Graph API resolution — see [Workspace administrators](#workspace-administrators) below and [Known limitations](#known-limitations) for the fallback behavior.

---

## Phase 2 — Fabric bootstrap details

[`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py) is the `postprovision` hook that runs after Bicep finishes. The 6 steps are listed in the main guide; the **Fabric-side** steps (3–6) are detailed below.

| Step | Module | What it does |
|---|---|---|
| 3 · `setup_workspace` | [`fabric/step_workspace_setup.py`](../../infra/scripts/fabric/step_workspace_setup.py) | Creates or finds the workspace (`Microsoft IQ - {solution_suffix}` by default; override with `FABRIC_WORKSPACE_NAME`). Assigns it to the Fabric capacity. **Auto-resumes a paused capacity** by issuing a [Microsoft.Fabric/capacities/resume](https://learn.microsoft.com/azure/templates/microsoft.fabric/capacities) call against `AZURE_SUBSCRIPTION_ID` / `AZURE_RESOURCE_GROUP` / `AZURE_FABRIC_CAPACITY_NAME`. |
| 4 · `setup_administrators` | [`fabric/step_workspace_admins.py`](../../infra/scripts/fabric/step_workspace_admins.py) | Adds workspace administrators from `AZURE_FABRIC_CAPACITY_ADMINISTRATORS` and `FABRIC_WORKSPACE_ADMINISTRATORS`. Tries Graph API resolution first; falls back to the **principal type detection** logic described in [Workspace administrators](#workspace-administrators). |
| 5 · `upload_installer` | [`fabric/step_notebook_installer.py`](../../infra/scripts/fabric/step_notebook_installer.py) | Reads [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) from disk, **patches it in-memory** with: (a) `GITHUB_BRANCH` set to `git branch --show-current` so the workspace is built from the same branch you're running `azd up` from; (b) `GITHUB_TOKEN` injected if the env var is set, enabling private-repo access. Then creates or updates the notebook in the workspace. |
| 6 · `run_installer` | [`fabric/step_notebook_installer.py`](../../infra/scripts/fabric/step_notebook_installer.py) | Submits the notebook as a Fabric job and polls for completion. Default timeout: 60 minutes. The notebook itself does the heavy lifting — see [Inside the installer notebook](#inside-the-installer-notebook). |

### Helper modules used by the Fabric steps

The bootstrap is intentionally thin: the four step modules above call into a small set of cross-cutting helpers under [`infra/scripts/common/`](../../infra/scripts/common/) and [`infra/scripts/fabric/`](../../infra/scripts/fabric/):

| Module | Role |
|---|---|
| [`common/config.py`](../../infra/scripts/common/config.py) | `SOLUTION_NAME = "Microsoft IQ"`, `default_workspace_name(suffix)` → `Microsoft IQ - {suffix}`. |
| [`common/env_utils.py`](../../infra/scripts/common/env_utils.py) | `get_required_env_var()`, `parse_workspace_administrators()` (combines capacity + workspace admin lists). |
| [`common/logging_config.py`](../../infra/scripts/common/logging_config.py) | `setup_logging()` honoring `LOG_LEVEL` (default `INFO`; set `DEBUG` for HTTP-level traces). |
| [`common/step_printer.py`](../../infra/scripts/common/step_printer.py) | `print_step()`, `print_steps_summary()` — the boxed banners in the deployment output. |
| [`fabric/fabric_api.py`](../../infra/scripts/fabric/fabric_api.py) | Fabric REST client (workspaces, notebooks, roles, long-running operations). |
| [`fabric/graph_api.py`](../../infra/scripts/fabric/graph_api.py) | Graph API client for principal resolution. |

### Idempotency

All four Fabric steps are safe to re-run:

- `setup_workspace` finds the existing workspace by name and skips creation; capacity assignment is a no-op when already correct.
- `setup_administrators` skips principals already on the role.
- `upload_installer` updates the existing notebook in place (matching by name).
- `run_installer` submits a fresh job each time. Re-running pulls the latest workspace items from GitHub, refreshing notebooks/reports/data agents and **preserving lakehouse data** (sample data is re-uploaded only if missing).

---

## Inside the installer notebook

[`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) executes **inside the Fabric workspace**. It does not run locally. Its responsibilities:

1. **Install dependencies** via `%pip install fabric-launcher --quiet` plus a few helpers. The local `requirements.txt` is irrelevant here — the notebook uses the Fabric runtime.
2. **Download the solution from GitHub** using [`fabric-launcher`](https://github.com/microsoft/fabric-launcher) — owner/repo/branch are configurable in the first notebook cell, set automatically by `upload_installer` to match your current git branch.
3. **Deploy standard Fabric items** from [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/) using [Fabric Git integration](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration). The deployment is **staged** (controlled by `item_type_stages`) so dependencies resolve in the right order: Lakehouse → Notebook → SemanticModel → Report.
4. **Run `pipeline_main`** to ingest sample CSVs from [`src/fabric/datagen/`](../../src/fabric/datagen/) into the `miqsadata` lakehouse tables.
5. **Deploy ontology items** from [`src/fabric/definitions/`](../../src/fabric/definitions/) using custom logic (Fabric Git integration does not yet support ontologies). Includes logical-ID resolution and lakehouse SQL endpoint mapping; replaces hardcoded source GUIDs (`SOURCE_WORKSPACE_ID`, `SOURCE_LAKEHOUSE_ID`) with the runtime values.
6. **Move items into folders** (`data_agent/`, `dashboards/`, `lakehouses/`, `notebooks/`, `ontology/`) for a clean workspace layout.

Configurable variables in the notebook's first cell:

| Variable | Default | Purpose |
|---|---|---|
| `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_BRANCH` | `microsoft` / `microsoft-iq-solution-accelerator` / current branch | Source repository. Patched at upload time. |
| `GITHUB_FABRIC_WORKSPACE_PATH` | `src/fabric/fabric_workspace` | Folder containing standard items. |
| `LAKEHOUSE_NAME` | `miqsadata` | Target lakehouse for data ingestion. |
| `DATA_FOLDERS` | (mapping) | Source data folders → lakehouse target paths. |
| `ONTOLOGY_NAMES`, `ONTOLOGY_TARGET_FOLDER` | `RetailSupplyChainOntologyModel` → `ontology/` | Ontology deployment. |
| `item_type_stages` | Lakehouse → Notebook/SemanticModel/Report | Deployment ordering. |

---

## Fabric workspace contents

After deployment, the workspace `Microsoft IQ - {solution_suffix}` (or your `FABRIC_WORKSPACE_NAME` override) contains the items below. The main guide shows a tree summary; this section adds detail.

### Lakehouse — `miqsadata`

A single [Fabric lakehouse](https://learn.microsoft.com/fabric/data-engineering/lakehouse-overview) with [shortcut](https://learn.microsoft.com/fabric/onelake/onelake-shortcuts-overview) support. Manages **25 tables across 6 business domains plus a shared date dimension**:

| Domain | Tables |
|---|---|
| **Customer** (5) | `Customer`, `CustomerTradeName`, `CustomerRelationshipType`, `Location`, `CustomerAccount` |
| **Product** (3) | `ProductLine`, `Product`, `ProductCategory` |
| **Sales** (3) | `Order`, `OrderLine`, `OrderPayment` |
| **Finance** (3) | `invoice`, `account`, `payment` |
| **Inventory** (6) | `Warehouses`, `Inventory`, `InventoryTransactions`, `PurchaseOrders`, `PurchaseOrderItems`, `DemandForecast` |
| **Supply chain** (4) | `Suppliers`, `ProductSuppliers`, `SupplyChainEvents`, `SupplyChainEventImpacts` |
| **Shared** (1) | `DimDate` |

Sample CSVs are uploaded during deployment and ingested by `pipeline_main`.

### Notebooks (26)

Organized under `notebooks/` by function:

| Folder | Count | Contents |
|---|---|---|
| `data_management/` | 4 | `create_scheme_tables`, `drop_all_tables`, `load_data_all_tables`, `truncate_all_tables` |
| `data_processing/` | 7 | `load_customer`, `load_finance`, `load_inventory`, `load_product`, `load_sales`, `load_supplychain`, `load_shared` |
| `query_samples/` | 4 | `get_data_summary`, `list_schema_tables`, `order_counts`, `sql_order_counts` |
| `schema/` | 7 | `model_customer`, `model_finance`, `model_inventory`, `model_product`, `model_sales`, `model_supplychain`, `model_shared` |
| (root) | 4 | `pipeline_main` (orchestrator), `pipeline_update`, `reset_or_debug`, `sampe_data_query` |

### AI data agent

| Agent | Purpose |
|---|---|
| `RetailSC Ontology Agent` | [Fabric Data Agent](https://learn.microsoft.com/fabric/data-science/ai-agents-overview) for natural language querying through the ontology semantic model. |

> The accelerator also supports lakehouse-based and entity-model-based data agent approaches that can be configured manually. See [`docs/fabric/fabric_data_agent/README.md`](./fabric_data_agent/README.md).

### Ontology and semantic models

| Item | Type | Purpose |
|---|---|---|
| `RetailSupplyChainOntologyModel` | [Ontology](https://learn.microsoft.com/fabric/data-science/ontology) | Business-friendly semantic layer over the lakehouse. |
| `RetailSupplyChainModel` | Semantic Model | Underlying semantic model used to generate the ontology. |
| `Sales Overview` | Semantic Model + Power BI Report | Sales analytics dashboard. |
| `Supply Chain Management` | Semantic Model + Power BI Report | Supply chain analytics dashboard. |

---

## Workspace administrators

`setup_administrators` accepts two combined sources:

- `AZURE_FABRIC_CAPACITY_ADMINISTRATORS` — JSON array, populated automatically from Bicep outputs. **Do not set manually.**
- `FABRIC_WORKSPACE_ADMINISTRATORS` — comma-separated list of additional admins. Set via `azd env set FABRIC_WORKSPACE_ADMINISTRATORS "..."` before `azd up`.

### Accepted identity formats

| Format | Example | Notes |
|---|---|---|
| User Principal Name (UPN) | `user@contoso.com` | Resolved via Microsoft Graph. Requires Graph API permissions on the deployment identity. |
| Object ID (GUID) | `87654321-4321-4321-4321-210987654321` | Direct assignment, no Graph lookup. **Recommended for service-principal / CI/CD deployments.** |
| Mixed | `user@contoso.com, 87654321-...` | Both formats can be combined in the same list. |

Get object IDs from the Azure CLI:

```bash
# User
az ad user show --id user@contoso.com --query id -o tsv
# Service principal
az ad sp show --id <app-id> --query id -o tsv
```

### Fallback behavior (no Graph access)

If the deployment identity cannot resolve the principal via Graph, [`step_workspace_admins.py`](../../infra/scripts/fabric/step_workspace_admins.py) tries both `User` and `ServicePrincipal` types automatically. See [Known limitations](#known-limitations) for the full picture.

---

## Fabric capacity SKU guidance

The default `FABRIC_CAPACITY_SKU_NAME` is `F2`. Override via `azd env set FABRIC_CAPACITY_SKU_NAME <SKU>` before `azd up`. SKU only applies when the deployment **creates** a capacity — when `AZURE_EXISTING_FABRIC_CAPACITY_NAME` is set, the SKU setting is ignored.

| Range | Use case |
|---|---|
| `F2` – `F4` | Development and evaluation. Sufficient to run the installer notebook end-to-end with sample data. |
| `F8` – `F32` | Small to medium production workloads. |
| `F64` – `F256` | Large enterprise workloads. |
| `F512` – `F2048` | High-performance analytics and data science. |

For sizing details see [Fabric capacity planning](https://learn.microsoft.com/fabric/admin/capacity-planning) and the [Fabric pricing page](https://azure.microsoft.com/pricing/details/microsoft-fabric/).

---

## Known limitations

### 1. Graph API principal lookup may fail for service principals

**Symptom**: `setup_administrators` logs `Graph API lookup failed for '<UPN>': <error>`; the script then falls back to trying both `User` and `ServicePrincipal` types blindly.

**Why**: Service principals deploying via OIDC often lack Graph `User.Read.All` / `Directory.Read.All` permissions and cannot resolve UPNs to object IDs.

**Fix**: Use object IDs instead of UPNs for `FABRIC_WORKSPACE_ADMINISTRATORS` (and any `fabricAdminMembers` Bicep parameter):

```bash
azd env set FABRIC_WORKSPACE_ADMINISTRATORS "87654321-4321-4321-4321-210987654321, 12345678-1234-1234-1234-123456789012"
azd up
```

### 2. Fabric REST API authorization (HTTP 401)

**Symptom**: `install_microsoft_iq_solution.py` exits with a warning block linking to Fabric licensing and identity-support docs.

**Why**: The deployment identity is missing one of:

- A Fabric license assignment ([Microsoft Fabric licenses](https://learn.microsoft.com/fabric/enterprise/licenses)).
- The tenant setting that allows service principals to call the Fabric APIs ([Identity support](https://learn.microsoft.com/rest/api/fabric/articles/identity-support), [Create Entra app](https://learn.microsoft.com/rest/api/fabric/articles/get-started/create-entra-app)).

The script exits with code 0 (graceful) so you can fix permissions and re-run `azd up`.

### 3. Notebook execution timeouts (`run_installer`)

**Symptom**: After 60 minutes, deployment fails with one of:

```
SparkCoreError/Other: Livy session has failed.
```

```
Operation 'Run notebook 'fabric_solution_installer' (...)' timed out after 60m 0s
```

**Why**: Transient Fabric platform issues — Spark session provisioning, managed VNet connectivity, or notebook scheduler latency. Not configuration-specific.

**Fix**: Re-run `azd up`. The deployment is idempotent and resumes from the failed step. Timeouts typically succeed on the next attempt.

### 4. Re-running deletes user-modified notebooks

**Symptom**: Edits to deployed notebooks are lost after `azd up`.

**Why**: `run_installer` re-deploys items from `src/fabric/fabric_workspace/` and overwrites in-place.

**Fix**: For experimentation, copy notebooks to a personal folder before editing, or fork the repo and modify the source.

---

## Additional resources

- [Top-level Deployment Guide](../DeploymentGuide.md) — the standard `azd up` walkthrough.
- [Manual notebook-only deployment](./DeploymentGuideFabricManual.md) — Fabric workspace alone, no Azure infrastructure or Foundry resources.
- [Microsoft Fabric documentation](https://learn.microsoft.com/fabric/)
- [Fabric REST APIs](https://learn.microsoft.com/rest/api/fabric/)
- [Fabric Git integration](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration)
- [Solution accelerator repository](https://github.com/microsoft/microsoft-iq-solution-accelerator)
