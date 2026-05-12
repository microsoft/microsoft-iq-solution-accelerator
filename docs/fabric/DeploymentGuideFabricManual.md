# Manual Deployment Guide — Fabric workspace only

This guide imports and runs [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) directly in a Microsoft Fabric workspace. **No `azd`, no Bicep, no local scripts** — and **no Foundry resources** are deployed.

## When to use this option

Use this guide if any of the following applies:

- You already have a Fabric capacity and only want the **Fabric workspace contents** (lakehouse, notebooks, semantic models, ontology, data agent).
- You don't want to install `azd` or PowerShell, or run the local Python deployment scripts.
- You're evaluating the solution and want the fastest portal-only path.

> **Important — what is *not* deployed**
>
> This option does **not** create any Azure resources outside Fabric. In particular, it does **not** deploy:
>
> - The Microsoft Foundry hub/project, Azure AI Search, Azure Storage, Azure OpenAI deployments, or the `ChatAgent` agent.
> - The Knowledge Base / Knowledge Source / KB MCP connection covered in [`DeploymentGuide.md`](../DeploymentGuide.md) §5.
>
> If you want the full data + AI experience (Fabric IQ + Microsoft Foundry), use the [top-level Deployment Guide](../DeploymentGuide.md) instead.

## Prerequisites

- A **Microsoft Fabric capacity** (paid F-SKU or trial) on the tenant.
- A **Fabric workspace** assigned to that capacity, plus permission to create and manage workspace items.
- Internet access from the Fabric runtime — the installer notebook downloads source code from GitHub via [`fabric-launcher`](https://github.com/microsoft/fabric-launcher).
- (Optional) A **GitHub Personal Access Token** with `repo` scope and `Contents: read` if you forked the accelerator as a private repository.

## Install in three steps

### 1 · Create a Fabric workspace

1. Sign in to [Microsoft Fabric](https://app.fabric.microsoft.com).
2. **Workspaces** → **+ New workspace**.
3. Give it a name (e.g., `Microsoft IQ`) and assign a Fabric capacity.
4. Click **Apply**.

### 2 · Download the installer notebook

Download [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) from the repository (right-click → *Save link as…* on GitHub) and save it locally as a `.ipynb` file.

### 3 · Import and run the notebook in Fabric

1. In your workspace, **+ New item** → **Import notebook** → upload the `.ipynb` file you just downloaded.
2. Open the notebook. In the first configuration cell, optionally edit:
   - `GITHUB_BRANCH` — defaults to `"main"`. Change it to deploy from a fork or feature branch.
   - `GITHUB_TOKEN` — paste your PAT here if your fork is private.
3. Click **Run all**.

The notebook installs `fabric-launcher`, downloads items from [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/) and ontology definitions from [`src/fabric/definitions/`](../../src/fabric/definitions/), runs `pipeline_main` to ingest sample data, then deploys the ontology and organizes items into folders.

For a detailed breakdown of what the installer does internally, see *[Inside the installer notebook](./DeploymentGuideFabric.md#inside-the-installer-notebook)* in the Fabric deep-dive guide.

## Verification

After the notebook completes, the workspace should contain:

- **Lakehouse** `miqsadata` — 25 tables across 6 business domains plus `DimDate`, with sample CSVs loaded under *Files*.
- **26 notebooks** under `data_management/`, `data_processing/`, `query_samples/`, `schema/`, plus `pipeline_main` / `pipeline_update` / `reset_or_debug` / `sampe_data_query` at the root.
- **AI data agent** `RetailSC Ontology Agent` for natural-language querying through the ontology.
- **Ontology** `RetailSupplyChainOntologyModel` and **semantic models** `RetailSupplyChainModel`, `Sales Overview`, `Supply Chain Management`.
- **Power BI reports** `Sales Overview` and `Supply Chain Management`.

The full inventory and table-level breakdown is documented in [Fabric workspace contents](./DeploymentGuideFabric.md#fabric-workspace-contents).

## Troubleshooting

| Issue | Likely cause | Resolution |
|---|---|---|
| Notebook import fails | Wrong file format | Make sure you downloaded the raw `.ipynb` file, not GitHub's HTML page. |
| Workspace capacity error | No capacity assigned | Assign a Fabric capacity (or trial) in **Workspace settings**. |
| `pipeline_main` Spark session fails | Transient Fabric platform issue | Re-run the failed cell. See [Known limitations](./DeploymentGuideFabric.md#known-limitations) §3. |
| `fabric-launcher` cannot download repo | Private fork without `GITHUB_TOKEN` | Set `GITHUB_TOKEN` in the configuration cell and re-run from that cell. |
| Items missing after run | Some cells did not finish | Confirm every cell shows a green check; re-run any that errored. |

## Cleanup

Delete the workspace from the Fabric portal:

1. [Microsoft Fabric](https://app.fabric.microsoft.com) → open the workspace.
2. **Workspace settings** → scroll to **Delete this workspace**.

> Deleting the workspace permanently removes all items inside it. The Fabric capacity itself (and any other Azure resource) is unaffected.

## Next steps

- For a fully automated end-to-end deployment that also provisions Foundry, the chat agent, and the knowledge base, switch to the [top-level Deployment Guide](../DeploymentGuide.md).
- For Fabric internals (bootstrap step modules, installer notebook configuration, capacity SKU sizing, known limitations), see the [Fabric deep-dive](./DeploymentGuideFabric.md).
- Microsoft Fabric documentation: [learn.microsoft.com/fabric](https://learn.microsoft.com/fabric/).
