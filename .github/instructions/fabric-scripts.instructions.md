---
description: "Use when editing Python files under infra/scripts/fabric/ or the fabric_solution_installer.ipynb notebook. Covers module architecture, deployment flow, logging conventions, environment variables, and documentation sync with DeploymentGuideFabric.md and DeploymentGuideFabricManual.md."
applyTo: "infra/scripts/fabric/**/*.py, infra/fabric/deploy/fabric_solution_installer.ipynb"
---

# Fabric deployment scripts and installer notebook — conventions and documentation sync

## Module architecture

```text
infra/scripts/fabric/
├── install_fabric_solution.py    # Entry-point: azd postprovision hook (4-step bootstrap)
├── remove_fabric_solution.py     # Entry-point: azd predown hook (workspace removal)
├── fabric_api.py                 # Fabric REST API client (workspaces, notebooks, roles, LROs)
├── graph_api.py                  # Graph API client (user/SP resolution)
└── helpers/
    ├── logging_config.py         # setup_logging(), _EmojiFormatter
    ├── config.py                 # SOLUTION_NAME, REPO_ROOT, default_workspace_name()
    ├── utils.py                  # File I/O, env vars, notebook encoding, step formatting
    ├── workspace.py              # setup_workspace() — create/find workspace, resume capacity
    └── workspace_admins.py       # setup_workspace_administrators() — Graph API + fallback
```

### Entry-point vs library modules

- **Entry-point scripts** (`install_fabric_solution.py`, `remove_fabric_solution.py`)
  call `setup_logging()` once at startup before other imports.
- **Library modules** (`fabric_api.py`, `graph_api.py`, `helpers/*.py`) never call
  `setup_logging()`. They only acquire loggers via `logging.getLogger(__name__)`.

### Key constants and environment variables

From [`helpers/config.py`](../../infra/scripts/fabric/helpers/config.py):
- `SOLUTION_NAME = "Microsoft IQ"`
- `default_workspace_name(suffix)` → `"Microsoft IQ - {suffix}"`

Required env vars (set by azd/Bicep outputs — do not set manually):
`AZURE_FABRIC_CAPACITY_NAME`, `SOLUTION_SUFFIX`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `AZURE_FABRIC_CAPACITY_ADMINISTRATORS`

Optional env vars (user-configurable):
`FABRIC_WORKSPACE_NAME`, `FABRIC_WORKSPACE_ADMINISTRATORS`, `FABRIC_WORKSPACE_ID`, `GITHUB_TOKEN`, `LOG_LEVEL`

### Deployment flow

[`install_fabric_solution.py`](../../infra/scripts/fabric/install_fabric_solution.py) runs 4 steps:
1. `setup_workspace` — create/find workspace, assign capacity, resume if paused (via [`workspace.py`](../../infra/scripts/fabric/helpers/workspace.py))
2. `setup_administrators` — add admins with Graph API resolution + fallback (via [`workspace_admins.py`](../../infra/scripts/fabric/helpers/workspace_admins.py))
3. `upload_installer` — upload [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) (create or update)
4. `run_installer` — execute notebook as Fabric job; notebook uses [fabric-launcher](https://github.com/microsoft/fabric-launcher) to deploy items from [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/) via [Fabric Git integration](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration)

[`remove_fabric_solution.py`](../../infra/scripts/fabric/remove_fabric_solution.py) runs as `azd down` predown hook: looks up workspace by name or `FABRIC_WORKSPACE_ID`, deletes it unattended, exits 0 on all errors.

### Installer notebook

[`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) is the orchestration notebook uploaded and executed by step 3-4 of `install_fabric_solution.py`. 

**Important: Runtime environment**
- The notebook runs **in the Fabric workspace**, not locally
- It manages its own dependencies via `%pip install fabric-launcher --quiet` in the notebook itself
- The local `requirements.txt` does **not** affect the notebook's execution environment
- The notebook uses the Fabric runtime's built-in packages plus what it installs via `%pip`

**Deployment workflow:**
The notebook uses [fabric-launcher](https://github.com/microsoft/fabric-launcher) to:
- Download source code from the GitHub repository
- Deploy Fabric items from [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/)
- Load sample data into the lakehouse
- Execute post-deployment tasks (run pipeline_main notebook, deploy ontology, move items to folders)

**Key configuration in the notebook:**
- `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_BRANCH` — source repository settings
- `GITHUB_FABRIC_WORKSPACE_PATH` — path to workspace items in repo (default: `"src/fabric/fabric_workspace"`)
- `LAKEHOUSE_NAME` — target lakehouse for data ingestion (default: `"miqsadata"`)
- `DATA_FOLDERS` — mapping of source data folders to lakehouse target paths
- `ONTOLOGY_NAMES` — list of ontology names to deploy from the repository
- `ONTOLOGY_TARGET_FOLDER` — target folder where ontologies will be moved after deployment
- `SOURCE_DEV_WORKSPACE_ID` — hardcoded GUID from source DEV workspace for replacement during ontology deployment
- `SOURCE_DEV_LAKEHOUSE_ID` — hardcoded GUID from source DEV lakehouse for replacement during ontology deployment
- `item_type_stages` — deployment order (Lakehouse/Ontology first, then Notebook/DataAgent)

**When modifying the installer notebook:**
- Changes to configuration defaults (workspace path, lakehouse name, data folders) require updates to both deployment guides
- Changes to deployment stages or post-deployment tasks require updates to §2 and §5 of `DeploymentGuideFabric.md`
- Changes to fabric-launcher API calls or parameters require updates to the manual guide's troubleshooting section
- Changes to `%pip install` dependencies in the notebook require updates to prerequisites in both deployment guides

## Documentation and instructions sync

When modifying scripts in this folder, check and update **both** the deployment guides and the copilot instruction files:

### Deployment guides

- [`docs/fabric/DeploymentGuideFabric.md`](../../docs/fabric/DeploymentGuideFabric.md) — Automated deployment guide (`azd`). Sections: §1 Prerequisites, §2 Deployment Overview (two-phase architecture, helper module table, idempotency), §3 Deployment Options (6 environments), §4 Deployment Commands, §5 Deployment Results (Azure resources + Fabric Components), §6 Advanced Configuration (infra, workspace, admin, optional vars, Python env), §7 Known Limitations, §8 Environment Cleanup, §9 Additional Resources.
- [`docs/fabric/DeploymentGuideFabricManual.md`](../../docs/fabric/DeploymentGuideFabricManual.md) — Manual portal-only guide. Import and run [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) directly in Fabric. Sections: prerequisites, 3-step install, verification, troubleshooting, cleanup, next steps.

### CI/CD workflow

- [`.github/workflows/azure-dev.yml`](../../.github/workflows/azure-dev.yml) — GitHub Actions pipeline (build → deploy → cleanup). Uses `azd up` / `azd down` which trigger the hooks in [`azure.yaml`](../../azure.yaml). The deployment summary step references the solution name (`Microsoft IQ`), default workspace name format (`Microsoft IQ - {suffix}`), deployed item descriptions, and documentation links. Keep these aligned when names, workspace defaults, or deployed items change.

### Project configuration files

- [`azure.yaml`](../../azure.yaml) — azd project config. Defines `postprovision` (install) and `predown` (remove) hooks that invoke [`Run-PythonScript.ps1`](../../infra/scripts/utils/Run-PythonScript.ps1) with the script path. Update when script paths change, scripts are added/removed, or hook behavior changes (e.g., new flags for `Run-PythonScript.ps1`).
- [`requirements.txt`](../../requirements.txt) — Python dependencies for **local scripts only** (`infra/scripts/fabric/`). Does **not** affect the installer notebook, which runs in Fabric and manages its own dependencies via `%pip install`. Update when adding, removing, or changing a package import in the local Python scripts. Current deps: `azure-identity`, `requests`, `azure-mgmt-fabric`.

### Copilot instruction files

After any change to `infra/scripts/fabric/` **or `infra/fabric/deploy/fabric_solution_installer.ipynb`**, review these instruction files and update them if the change affects the documented architecture, module list, env vars, deployment flow, installer configuration, or logging conventions:

- [`.github/instructions/fabric-scripts.instructions.md`](./fabric-scripts.instructions.md) — this file (module architecture, deployment flow, env vars, logging)
- [`.github/instructions/fabric-deployment-docs.instructions.md`](./fabric-deployment-docs.instructions.md) — deployment guide structure, relative paths, source of truth
- [`.github/instructions/fabric-workspace.instructions.md`](./fabric-workspace.instructions.md) — workspace item inventory (if installer notebook changes affect deployed items)

| Script change | Update in docs |
|---|---|
| New/renamed environment variable | §6 Advanced Configuration tables |
| Changed deployment steps in `main()` | §2 Deployment Overview — Phase 2 |
| Changed error handling / exit behavior | §7 Known Limitations or §8 Cleanup |
| Changed helper module API | §2 Deployment Architecture table |
| Changed workspace naming / defaults | §6 Workspace Settings table + `azure-dev.yml` summary |
| Changed admin handling logic | §6 Admin Assignment + §7 Graph API Limitation |
| Changed notebook upload/run logic | §2 Phase 2 steps 3-4 + manual guide step 3 |
| Changed installer notebook reference | Both guides: notebook links |
| Changed solution name or branding | `azure-dev.yml` summary + both deployment guides |
| Changed deployed items (lakehouse, notebooks, agents) | `azure-dev.yml` summary + §5 Fabric Components |
| Added/removed/changed Python dependency in local scripts | `requirements.txt` (does NOT affect installer notebook) |
| Renamed or moved a script file | `azure.yaml` hooks + `azure-dev.yml` if referenced |
| Changed `Run-PythonScript.ps1` flags | `azure.yaml` hooks + §6 Python Environment |
| **Installer notebook changes:** | |
| Changed GitHub source settings (owner/repo/branch/path) | §2 Phase 2 step 3 + manual guide §2 Prerequisites |
| Changed lakehouse name or data folder mappings | §5 Fabric Components + manual guide §3 Run Installer |
| Changed fabric-launcher configuration (stages, validation) | §2 Phase 2 step 3 + §5 Fabric Components + manual guide §4 Verify |
| Added/removed post-deployment tasks (notebooks, ontology) | §2 Phase 2 step 4 + §5 Fabric Components |
| Changed `%pip install` dependencies in notebook | §1 Prerequisites (both guides) — notebook runs in Fabric, not local env |
| Changed notebook cell structure or markdown instructions | Manual guide §3 Run Installer + §4 Verify |
| Changed notebook execution parameters or timeout | §2 Phase 2 step 4 + manual guide §5 Troubleshooting |

### Relative paths used in the docs (from `docs/fabric/`)

- Scripts: `../../infra/scripts/fabric/install_fabric_solution.py`, `../../infra/scripts/fabric/remove_fabric_solution.py`
- Helpers: `../../infra/scripts/fabric/helpers/workspace.py`, `workspace_admins.py`, `utils.py`
- Installer notebook: `../../infra/fabric/deploy/fabric_solution_installer.ipynb`
- Workspace items: `../../src/fabric/fabric_workspace/`
- Repo root: `../../infra/main.bicep`, `../../azure.yaml`, `../../.github/workflows/azure-dev.yml`

## Fabric workspace items deployed by installer

The installer notebook ([`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb)) deploys items from [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/) using [fabric-launcher](https://github.com/microsoft/fabric-launcher). 

**When workspace items change** (items added/removed/renamed, or the folder structure in `src/fabric/fabric_workspace/` is modified), you must update:
- §5 (Deployment Results > Fabric Components) in `DeploymentGuideFabric.md`
- Verification section in `DeploymentGuideFabricManual.md`
- The installer notebook's `GITHUB_FABRIC_WORKSPACE_PATH` if the folder location changes
- The installer notebook's `item_type_stages` if deployment order needs adjustment
- `azure-dev.yml` deployment summary if the list of deployed components changes

**Current deployed items:**

- **1 lakehouse**: `miqsadata` — 22 tables across 6 domains (customer, product, sales, finance, inventory, supplychain), [shortcut](https://learn.microsoft.com/fabric/onelake/onelake-shortcuts-overview)-enabled
- **23 notebooks**: data_management (4), data_processing (6), query_samples (4), schema (6), root (3)
- **2 AI data agents**: `data_agent_lakehouse` (NL query over lakehouse), `data_agent_ontology` (ontology-based)
- **1 ontology model**: `ontology_semantic_model`

## Logging conventions

### Log level control

The log level is set by the `LOG_LEVEL` environment variable (default: `INFO`).
Users set it via `azd env set LOG_LEVEL DEBUG`.

### Using `logger` in library modules

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Visible at default level")
logger.debug("Only visible when LOG_LEVEL=DEBUG")
logger.warning("Always visible")
logger.error("Always visible")
```

Do not add handlers or set levels on module-level loggers.

### The `_log()` wrapper in API clients

`FabricApiClient._log()` and `GraphApiClient._log()` default to `level="DEBUG"`
so routine HTTP chatter is hidden at the default log level. Use explicit
`level="INFO"` only for messages the user should see during normal runs, such as
long-running operation progress. Use `level="WARNING"` or `level="ERROR"` for
actionable issues.

```python
self._log(f"Making request to {url}")                     # DEBUG (hidden by default)
self._log(f"Still running ({elapsed})", level="INFO")     # visible at default level
self._log(f"Rate limited", level="WARNING")               # visible at default level
```

### Emoji policy

Emojis appear **only on major section boundaries** to provide visual landmarks
without cluttering output:

| Where | Example |
|-------|---------|
| Banner / title | `🏭 Solution Installer`, `🗑️ Starting removal` |
| Top-level section header | `🔐 Authenticating clients…`, `👥 Setting up administrators` |
| Final completion line | `🎉 INSTALLATION COMPLETE!` |

**Do not** add emojis to sub-step detail lines, individual success confirmations,
or indented status messages. Keep those as plain text.

### Indentation convention

- Top-level messages: no indent.
- Sub-steps within a section: 3-space indent (`"   "`).
- Detail lines within a sub-step: 6-space indent (`"      "`).

```python
logger.info("🔐 Authenticating clients…")       # section header, no indent
logger.info("   Fabric API client authenticated") # sub-step, 3 spaces
logger.info("      Status: Completed")            # detail, 6 spaces
```

### Third-party logger suppression

`setup_logging()` pins `azure`, `urllib3`, `requests`, and `msal` loggers to
WARNING. If adding a new noisy dependency, suppress it the same way in
[`helpers/logging_config.py`](../../infra/scripts/fabric/helpers/logging_config.py).
