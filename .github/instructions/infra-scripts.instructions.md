---
description: "Use when editing Python files under infra/scripts/common/, infra/scripts/fabric/, infra/scripts/foundry/, the entry-point scripts, or the fabric_solution_installer.ipynb notebook. Covers module architecture, deployment flow, logging conventions, environment variables, and documentation sync with DeploymentGuideFabric.md and DeploymentGuideFabricManual.md."
applyTo: "infra/scripts/common/**/*.py, infra/scripts/fabric/**/*.py, infra/scripts/foundry/**/*.py, infra/scripts/install_microsoft_iq_solution.py, infra/scripts/remove_microsoft_iq_solution.py, infra/fabric/deploy/fabric_solution_installer.ipynb"
---

# Fabric deployment scripts and installer notebook — conventions and documentation sync

## Module architecture

```text
infra/scripts/
├── install_microsoft_iq_solution.py  # Entry-point: azd postprovision hook (6-step bootstrap)
├── remove_microsoft_iq_solution.py   # Entry-point: azd predown hook (workspace removal)
├── common/                           # Package: cross-cutting helpers (azd, repo paths, env vars, PDFs)
│   ├── __init__.py
│   ├── config.py                     # SOLUTION_NAME, REPO_ROOT, DATA_DIR, default_workspace_name()
│   ├── logging_config.py             # setup_logging(), _EmojiFormatter
│   ├── env_utils.py                  # get_required_env_var, read_file_content,
│   │                                 # parse_workspace_administrators
│   ├── env.py                        # azd/.env loaders, get_required_env, get_data_folder
│   ├── pdf_utils.py                  # PDF extraction + sentence-aware chunking
│   └── step_printer.py               # print_step, print_steps_summary
├── fabric/                           # Package: Fabric REST clients and Fabric-domain step orchestration
│   ├── __init__.py
│   ├── fabric_api.py                 # Fabric REST API client (workspaces, notebooks, roles, LROs)
│   ├── graph_api.py                  # Graph API client (user/SP resolution)
│   ├── notebook_installer.py         # INSTALLER_NOTEBOOK_NAME, get_notebook_path, encode_notebook,
│   │                                 # upload_installer_notebook, run_installer_notebook
│   ├── workspace.py                  # setup_workspace() — create/find workspace, resume capacity
│   └── workspace_admins.py           # setup_workspace_administrators() — Graph API + fallback
└── foundry/                          # Package: Foundry / AI Search clients and step orchestration
    ├── __init__.py
    ├── search_api.py                 # Azure AI Search: index, knowledge source, knowledge base
    ├── blob_api.py                   # Azure Blob Storage upload helpers
    ├── agent_api.py                  # AI Foundry agent + KB MCP project connection
    ├── knowledge_base.py             # setup_knowledge_base() — search index + KS + KB
    └── agent_setup.py                # setup_agent() — agent + KB MCP connection
```

### Entry-point vs library modules

- **Entry-point scripts** (`install_microsoft_iq_solution.py`, `remove_microsoft_iq_solution.py`)
  call `setup_logging()` once at startup before other imports.
- **Library modules** (`common/*.py`, `fabric/*.py`, `foundry/*.py`) never call
  `setup_logging()`. They only acquire loggers via `logging.getLogger(__name__)`.
  Library modules use **absolute** package imports (`from common.config import …`,
  `from fabric.fabric_api import …`, `from foundry.search_api import …`); they never
  use `from ..` relative imports and never manipulate `sys.path`.

### Cross-package helpers (`common/`)

Anything that is not specific to a Fabric or Foundry REST surface lives in
`common/`. This includes solution / repo-path constants, azd environment
loaders, env-var parsing, file I/O, logging configuration, step header
formatting, and PDF chunking. Both domain packages and the entry-point
scripts import from here directly:

- [`common/config.py`](../../infra/scripts/common/config.py) — `SOLUTION_NAME = "Microsoft IQ"`, `REPO_ROOT`, `DATA_DIR` (Foundry data folder), and `default_workspace_name(suffix)` for the Fabric workspace name format.
- [`common/logging_config.py`](../../infra/scripts/common/logging_config.py) — `setup_logging()` with `LOG_LEVEL` env var support and `_EmojiFormatter`.
- [`common/env_utils.py`](../../infra/scripts/common/env_utils.py) — `get_required_env_var()`, `read_file_content()`, and `parse_workspace_administrators()` (combines `AZURE_FABRIC_CAPACITY_ADMINISTRATORS` and `FABRIC_WORKSPACE_ADMINISTRATORS`).
- [`common/env.py`](../../infra/scripts/common/env.py) — azd/.env loaders (`load_azd_env`, `load_project_env`, `load_all_env`), `get_required_env`, `get_data_folder`, `print_env_status`. Used by standalone Foundry scripts (e.g. `foundry/test_agent.py`) that run outside `azd`.
- [`common/pdf_utils.py`](../../infra/scripts/common/pdf_utils.py) — `extract_pages_from_pdf`, `chunk_text_by_sentences`, `process_pdfs_to_documents` (used by `setup_knowledge_base`).
- [`common/step_printer.py`](../../infra/scripts/common/step_printer.py) — `print_step()`, `print_steps_summary()`.

The domain packages (`fabric/`, `foundry/`) only contain modules that talk to
Fabric / Foundry REST APIs or orchestrate a deployment step on top of those
clients.

### Foundry-side step orchestration

`foundry/step_knowledge_base.py` (`setup_knowledge_base()`) and `foundry/step_agent_setup.py`
(`setup_agent()`) follow the same pattern as the Fabric-side `fabric/step_workspace_setup.py`
(`setup_workspace()`) and `fabric/step_workspace_admins.py`
(`setup_workspace_administrators()`): each is a single top-level function that the
entry-point script calls once, takes the config values it needs as parameters, owns
its file I/O (`ontology_config.json`, `search_ids.json`, `agent_ids.json`), and
raises on hard errors. Skip-when-not-configured logic stays in the entry point.

### Key constants and environment variables

From [`common/config.py`](../../infra/scripts/common/config.py):
- `SOLUTION_NAME = "Microsoft IQ"`
- `REPO_ROOT` — absolute path to the repository root
- `DATA_DIR` — repo-relative path to `src/foundry/data`
- `default_workspace_name(suffix)` → `"Microsoft IQ - {suffix}"`

Required env vars (set by azd/Bicep outputs — do not set manually):
`AZURE_FABRIC_CAPACITY_NAME`, `SOLUTION_SUFFIX`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `AZURE_FABRIC_CAPACITY_ADMINISTRATORS`

Optional env vars (user-configurable):
`FABRIC_WORKSPACE_NAME`, `FABRIC_WORKSPACE_ADMINISTRATORS`, `FABRIC_WORKSPACE_ID`, `GITHUB_TOKEN`, `LOG_LEVEL`

### Deployment flow

[`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py) runs 6 steps unconditionally (matching `ALL_DEPLOYMENT_STEPS`). All required env vars are sourced from `main.bicep` outputs via `azd`; the script aborts on the first step that raises:
1. `setup_knowledge_base` — create AI Search index, upload PDFs, create Foundry IQ knowledge source and knowledge base (via [`foundry/step_knowledge_base.py`](../../infra/scripts/foundry/step_knowledge_base.py))
2. `setup_agent` — create AI Foundry agent with Knowledge Base MCP tool (via [`foundry/step_agent_setup.py`](../../infra/scripts/foundry/step_agent_setup.py))
3. `setup_workspace` — create/find workspace, assign capacity, resume if paused (via [`fabric/step_workspace_setup.py`](../../infra/scripts/fabric/step_workspace_setup.py))
4. `setup_administrators` — add admins with Graph API resolution + fallback (via [`fabric/step_workspace_admins.py`](../../infra/scripts/fabric/step_workspace_admins.py))
5. `upload_installer` — upload [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) (create or update; via [`fabric/step_notebook_installer.py`](../../infra/scripts/fabric/step_notebook_installer.py)). The notebook is automatically patched before upload to:
   - Set `GITHUB_BRANCH` to the currently checked out git branch (detected via `git branch --show-current`)
   - Inject `GITHUB_TOKEN` if the environment variable is set (for private repository access)
6. `run_installer` — execute notebook as Fabric job (via [`fabric/step_notebook_installer.py`](../../infra/scripts/fabric/step_notebook_installer.py)); notebook uses [fabric-launcher](https://github.com/microsoft/fabric-launcher) to deploy items from [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/) via [Fabric Git integration](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration)

[`remove_microsoft_iq_solution.py`](../../infra/scripts/remove_microsoft_iq_solution.py) runs as `azd down` predown hook: looks up workspace by name or `FABRIC_WORKSPACE_ID`, deletes it unattended, exits 0 on all errors.

### Installer notebook

[`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) is the orchestration notebook uploaded and executed by step 3-4 of `install_microsoft_iq_solution.py`. 

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
- `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_BRANCH` — source repository settings. **Note**: When deployed via `install_microsoft_iq_solution.py`, `GITHUB_BRANCH` is automatically set to the currently checked out git branch
- `GITHUB_FABRIC_WORKSPACE_PATH` — path to workspace items in repo (default: `"src/fabric/fabric_workspace"`)
- `LAKEHOUSE_NAME` — target lakehouse for data ingestion (default: `"miqsadata"`)
- `DATA_FOLDERS` — mapping of source data folders to lakehouse target paths
- `ONTOLOGY_NAMES` — list of ontology names to deploy from the repository
- `ONTOLOGY_TARGET_FOLDER` — target folder where ontologies will be moved after deployment
- `SOURCE_WORKSPACE_ID` — hardcoded GUID from source DEV workspace for replacement during ontology deployment
- `SOURCE_LAKEHOUSE_ID` — hardcoded GUID from source DEV lakehouse for replacement during ontology deployment
- `item_type_stages` — deployment order (Lakehouse first, then Notebook/SemanticModel/Report)

**When modifying the installer notebook:**
- Changes to configuration defaults (workspace path, lakehouse name, data folders) require updates to both deployment guides
- Changes to deployment stages or post-deployment tasks require updates to §2 and §5 of `DeploymentGuideFabric.md`
- Changes to fabric-launcher API calls or parameters require updates to the manual guide's troubleshooting section
- Changes to `%pip install` dependencies in the notebook require updates to prerequisites in both deployment guides

## Documentation and instructions sync

When modifying scripts in this folder, check and update **both** the deployment guides and the copilot instruction files:

### Deployment guides

- [`docs/DeploymentGuide.md`](../../docs/DeploymentGuide.md) — **Top-level entry-point guide** (single `azd up` walkthrough). Sections: Introduction, Deployment Overview (Phases 1–2 with the 6 `step_*` modules listed in order), Deployment Commands, Optional Configuration Variables, Deployment Results (Fabric IQ + Foundry components), Environment Cleanup, Additional Resources. Keep it short — deeper details belong in `DeploymentGuideFabric.md`.
- [`docs/fabric/DeploymentGuideFabric.md`](../../docs/fabric/DeploymentGuideFabric.md) — Automated deployment guide (`azd`). Sections: §1 Prerequisites, §2 Deployment Overview (two-phase architecture, helper module table, idempotency), §3 Deployment Options (6 environments), §4 Deployment Commands, §5 Deployment Results (Azure resources + Fabric Components), §6 Advanced Configuration (infra, workspace, admin, optional vars, Python env), §7 Known Limitations, §8 Environment Cleanup, §9 Additional Resources.
- [`docs/fabric/DeploymentGuideFabricManual.md`](../../docs/fabric/DeploymentGuideFabricManual.md) — Manual portal-only guide. Import and run [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) directly in Fabric. Sections: prerequisites, 3-step install, verification, troubleshooting, cleanup, next steps.

### CI/CD workflow

- [`.github/workflows/azure-dev.yml`](../../.github/workflows/azure-dev.yml) — GitHub Actions pipeline (build → deploy → cleanup). Uses `azd up` / `azd down` which trigger the hooks in [`azure.yaml`](../../azure.yaml). The deployment summary step references the solution name (`Microsoft IQ`), default workspace name format (`Microsoft IQ - {suffix}`), deployed item descriptions, and documentation links. Keep these aligned when names, workspace defaults, or deployed items change.

### Project configuration files

- [`azure.yaml`](../../azure.yaml) — azd project config. Defines `postprovision` (install) and `predown` (remove) hooks that invoke [`Run-PythonScript.ps1`](../../infra/scripts/utils/Run-PythonScript.ps1) with the script path. Update when script paths change, scripts are added/removed, or hook behavior changes (e.g., new flags for `Run-PythonScript.ps1`).
- [`requirements.txt`](../../requirements.txt) — Python dependencies for **local scripts only** (`infra/scripts/common/`, `infra/scripts/fabric/`, and `infra/scripts/foundry/`). Does **not** affect the installer notebook, which runs in Fabric and manages its own dependencies via `%pip install`. Update when adding, removing, or changing a package import in the local Python scripts.

### Copilot instruction files

After any change to `infra/scripts/common/`, `infra/scripts/fabric/`, `infra/scripts/foundry/`, **or `infra/fabric/deploy/fabric_solution_installer.ipynb`**, review these instruction files and update them if the change affects the documented architecture, module list, env vars, deployment flow, installer configuration, or logging conventions:

- [`.github/instructions/infra-scripts.instructions.md`](./infra-scripts.instructions.md) — this file (module architecture, deployment flow, env vars, logging)
- [`.github/instructions/deployment-guide.instructions.md`](./deployment-guide.instructions.md) — top-level `docs/DeploymentGuide.md` structure, relative paths, source of truth
- [`.github/instructions/fabric-deployment-docs.instructions.md`](./fabric-deployment-docs.instructions.md) — deployment guide structure, relative paths, source of truth
- [`.github/instructions/fabric-workspace.instructions.md`](./fabric-workspace.instructions.md) — workspace item inventory (if installer notebook changes affect deployed items)

| Script change | Update in docs |
|---|---|
| New/renamed environment variable | `DeploymentGuide.md` §4 Optional Configuration Variables + `DeploymentGuideFabric.md` §6 Advanced Configuration tables |
| Changed deployment steps in `main()` (order, name, or `_warn_step` vs. `_abort` semantics) | `DeploymentGuide.md` §2 Phase 2 list + `DeploymentGuideFabric.md` §2 Deployment Overview Phase 2 |
| Changed error handling / exit behavior | `DeploymentGuideFabric.md` §7 Known Limitations or §8 Cleanup |
| Changed Fabric helper module API (`fabric/step_workspace_setup.py`, `fabric/step_workspace_admins.py`, `fabric/step_notebook_installer.py`) | `DeploymentGuide.md` §2 Phase 2 step links + `DeploymentGuideFabric.md` §2 Deployment Architecture table |
| Changed Foundry helper module API (`foundry/step_knowledge_base.py`, `foundry/step_agent_setup.py`) | `DeploymentGuide.md` §2 Phase 2 step links + `DeploymentGuideFabric.md` §2 Deployment Architecture table |
| Changed cross-cutting helper API (`common/config.py`, `common/logging_config.py`, `common/env_utils.py`, `common/env.py`, `common/pdf_utils.py`, `common/step_printer.py`) | `DeploymentGuideFabric.md` §2 Deployment Architecture table |
| Changed workspace naming / defaults | `DeploymentGuide.md` §5 Fabric IQ Components workspace tree + `DeploymentGuideFabric.md` §6 Workspace Settings table + `azure-dev.yml` summary |
| Changed admin handling logic | `DeploymentGuideFabric.md` §6 Admin Assignment + §7 Graph API Limitation |
| Changed notebook upload/run logic | `DeploymentGuide.md` §2 Phase 2 steps 5-6 + `DeploymentGuideFabric.md` §2 Phase 2 steps 5-6 + manual guide step 3. **Note**: Automatic git branch detection and GITHUB_BRANCH patching (added 2026-04) ensures the notebook downloads from the currently checked out branch |
| Changed installer notebook reference | All three deployment guides: notebook links |
| Changed solution name or branding | `azure-dev.yml` summary + all three deployment guides |
| Changed deployed items (lakehouse, notebooks, agents) | `azure-dev.yml` summary + `DeploymentGuide.md` §5 Fabric IQ Components + `DeploymentGuideFabric.md` §5 Fabric Components |
| Changed Foundry resource naming (search index, KB, agent) | `DeploymentGuide.md` §5 Microsoft Foundry Components |
| Added/removed/changed Python dependency in local scripts | `requirements.txt` (does NOT affect installer notebook) |
| Renamed or moved a script file | `azure.yaml` hooks + `azure-dev.yml` if referenced + `pyrightconfig.json` `extraPaths` (only if `infra/scripts/` itself moves) |
| Changed `Run-PythonScript.ps1` flags | `azure.yaml` hooks + `DeploymentGuideFabric.md` §6 Python Environment |
| Changed cleanup behavior (`remove_microsoft_iq_solution.py` or `predown` hook) | `DeploymentGuide.md` §6 Environment Cleanup + `DeploymentGuideFabric.md` §8 Environment Cleanup |
| **Installer notebook changes:** | |
| Changed GitHub source settings (owner/repo/branch/path) | `DeploymentGuideFabric.md` §2 Phase 2 step 5 + manual guide §2 Prerequisites |
| Changed lakehouse name or data folder mappings | `DeploymentGuide.md` §5 Fabric IQ Components + `DeploymentGuideFabric.md` §5 Fabric Components + manual guide §3 Run Installer |
| Changed fabric-launcher configuration (stages, validation) | `DeploymentGuideFabric.md` §2 Phase 2 step 5 + §5 Fabric Components + manual guide §4 Verify |
| Added/removed post-deployment tasks (notebooks, ontology) | `DeploymentGuideFabric.md` §2 Phase 2 step 6 + §5 Fabric Components |
| Changed `%pip install` dependencies in notebook | `DeploymentGuideFabric.md` §1 Prerequisites + manual guide prerequisites — notebook runs in Fabric, not local env |
| Changed notebook cell structure or markdown instructions | Manual guide §3 Run Installer + §4 Verify |
| Changed notebook execution parameters or timeout | `DeploymentGuideFabric.md` §2 Phase 2 step 6 + manual guide §5 Troubleshooting |

### Relative paths used in the docs (from `docs/fabric/`)

- Entry-point scripts: `../../infra/scripts/install_microsoft_iq_solution.py`, `../../infra/scripts/remove_microsoft_iq_solution.py`
- Fabric helpers: `../../infra/scripts/fabric/step_workspace_setup.py`, `step_workspace_admins.py`, `step_notebook_installer.py`
- Foundry helpers: `../../infra/scripts/foundry/step_knowledge_base.py`, `step_agent_setup.py`, `search_api.py`, `blob_api.py`, `agent_api.py`
- Cross-cutting helpers: `../../infra/scripts/common/config.py`, `logging_config.py`, `env_utils.py`, `env.py`, `pdf_utils.py`, `step_printer.py`
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
[`common/logging_config.py`](../../infra/scripts/common/logging_config.py).
