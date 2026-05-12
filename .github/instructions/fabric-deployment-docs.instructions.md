---
description: "Use when editing deployment guides under docs/fabric/. Covers document structure, script and workspace references, relative link conventions, source of truth, and the no-duplication rule with docs/DeploymentGuide.md."
applyTo: "docs/fabric/Deployment*.md"
---

# Fabric deployment documentation — structure and references

## Documents

The two guides under [`docs/fabric/`](../../docs/fabric/) are **companions** to the top-level [`docs/DeploymentGuide.md`](../../docs/DeploymentGuide.md). They must not duplicate the content of the main guide.

### `DeploymentGuideFabric.md` — Fabric IQ deep-dive

A reference for users who need Fabric internals beyond what `azd up` exposes. Section structure:

1. **Header + path-selection table** — three rows: full automated deployment (link to [`DeploymentGuide.md`](../../docs/DeploymentGuide.md)), this guide, manual notebook-only ([`DeploymentGuideFabricManual.md`](../../docs/fabric/DeploymentGuideFabricManual.md)). The intro must point users back to `DeploymentGuide.md` for the standard walkthrough.
2. **Table of Contents** — `## Table of Contents` listing every other top-level section.
3. **Fabric-specific Prerequisites** — *only* what the main guide doesn't cover: `Microsoft.Fabric` resource provider, Fabric tenant settings (service principal API access), and the API permissions table (Fabric REST, Microsoft Graph, Power BI).
4. **Phase 2 — Fabric bootstrap details** — table of the 4 Fabric-side steps (3·`setup_workspace`, 4·`setup_administrators`, 5·`upload_installer`, 6·`run_installer`) with their modules and behavior. Followed by a *Helper modules used by the Fabric steps* table covering [`common/config.py`](../../infra/scripts/common/config.py), [`common/env_utils.py`](../../infra/scripts/common/env_utils.py), [`common/logging_config.py`](../../infra/scripts/common/logging_config.py), [`common/step_printer.py`](../../infra/scripts/common/step_printer.py), [`fabric/fabric_api.py`](../../infra/scripts/fabric/fabric_api.py), [`fabric/graph_api.py`](../../infra/scripts/fabric/graph_api.py); plus an *Idempotency* paragraph.
5. **Inside the installer notebook** — what [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) does inside Fabric: `%pip install fabric-launcher`, GitHub download, staged item deployment via `item_type_stages` (Lakehouse → Notebook → SemanticModel → Report), `pipeline_main` ingestion, ontology deployment from [`src/fabric/definitions/`](../../src/fabric/definitions/), folder organization. Includes a configurable-variables table (`GITHUB_OWNER`/`GITHUB_REPO`/`GITHUB_BRANCH`, `GITHUB_FABRIC_WORKSPACE_PATH`, `LAKEHOUSE_NAME`, `DATA_FOLDERS`, `ONTOLOGY_NAMES`, `item_type_stages`).
6. **Fabric workspace contents** — detailed inventory not in the main guide: `miqsadata` lakehouse with the per-domain table breakdown (Customer 5, Product 3, Sales 3, Finance 3, Inventory 6, Supply chain 4, Shared 1 = 25 tables); the 26 notebooks broken down by folder; the data agent `RetailSC Ontology Agent`; ontology + semantic models + reports.
7. **Workspace administrators** — accepted identity formats (UPN, object ID, mixed), `az ad user show` / `az ad sp show` snippets, and the fallback behavior. Fabric-specific.
8. **Fabric capacity SKU guidance** — F2–F4 dev, F8–F32 small/medium prod, F64–F256 large, F512–F2048 high-performance. Note that SKU is ignored when `AZURE_EXISTING_FABRIC_CAPACITY_NAME` is set.
9. **Known limitations** — Graph API principal lookup fallback, Fabric REST API authorization (HTTP 401), notebook execution timeouts (Spark/Livy + 60-min job timeout), and the "re-running overwrites user-modified notebooks" caveat.
10. **Additional resources** — links back to `DeploymentGuide.md`, the manual guide, Microsoft Fabric docs, Fabric REST APIs, Fabric Git integration, and the GitHub repo.

### `DeploymentGuideFabricManual.md` — Portal-only manual deployment

A short guide for deploying **only the Fabric workspace items** by importing [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) directly in Fabric. **No Azure infrastructure, no Foundry resources, no chat agent.** Section structure:

1. **Intro** — one-paragraph summary stating no `azd`/Bicep/local scripts are involved.
2. **When to use this option** — three bullets, followed by an **Important — what is *not* deployed** callout that explicitly lists Foundry hub/project, Azure AI Search, Storage, OpenAI, `ChatAgent`, Knowledge Base / Knowledge Source / KB MCP connection. Must redirect users wanting the full experience to [`DeploymentGuide.md`](../../docs/DeploymentGuide.md).
3. **Prerequisites** — Fabric capacity, workspace + permissions, internet from the Fabric runtime, optional `GITHUB_TOKEN`.
4. **Install in three steps** — Create workspace → Download notebook → Import & Run. The download step must link directly to [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb).
5. **Verification** — short bullet list (lakehouse + 26 notebooks + agent + ontology + semantic models + reports). Detailed breakdowns must link back to `DeploymentGuideFabric.md` *Fabric workspace contents* — do not duplicate them here.
6. **Troubleshooting** — table covering import failures, capacity errors, Spark transient failures (link to deep-dive *Known limitations*), private-fork token issues, partial-run recovery.
7. **Cleanup** — delete-workspace-from-portal flow with the warning that the Fabric capacity is unaffected.
8. **Next steps** — link to `DeploymentGuide.md` for the full automated path and `DeploymentGuideFabric.md` for internals.

## No-duplication rule

Both guides are **companions** to [`docs/DeploymentGuide.md`](../../docs/DeploymentGuide.md). They must not contain content already covered in the main guide.

| Belongs in the **main guide** ([`DeploymentGuide.md`](../../docs/DeploymentGuide.md)) | Belongs in `DeploymentGuideFabric.md` | Belongs in `DeploymentGuideFabricManual.md` |
|---|---|---|
| The 6-step Phase 2 table | The deep-dive on the 4 Fabric-side steps and their helper modules | (none) |
| Deployment environment options (Local, Codespaces, Dev Container, GitHub Actions) | (none) | (none) |
| `azd up` command block, optional configuration variables table, `azd down` cleanup | (none) | The manual 3-step portal flow only |
| High-level workspace tree (lakehouse, notebooks, ontology, semantic models, agent) | The detailed table-level breakdown (25 tables, 26 notebooks by folder) | A short bullet list — link back to the deep-dive for details |
| Foundry components and verification | (none — this guide is Fabric-only) | (explicit "what is *not* deployed" callout listing Foundry pieces) |

Hard rules:

- **Do not** restate `azd` prerequisites (`azd`, Python, PowerShell), the `azd up` command, the optional configuration variables table, or `azd down` in either Fabric guide.
- **Do not** duplicate the Foundry components table or the *Verify in the Foundry portal* checklist — those live solely in [`DeploymentGuide.md`](../../docs/DeploymentGuide.md) §6.
- **Do** link back to specific anchors in the main guide and the deep-dive when summarising shared content.
- **Do** keep the deep-dive guide focused on *content the main guide intentionally omits* (helper modules, installer notebook internals, table-level inventory, SKU sizing, Fabric-specific known limitations).

## Relative path conventions

These docs live at `docs/fabric/`. Relative paths from this location:

| Target | Relative path |
|---|---|
| Main deployment guide | `../DeploymentGuide.md` |
| Sibling guide | `./DeploymentGuideFabric.md` or `./DeploymentGuideFabricManual.md` |
| Install entry point | `../../infra/scripts/install_microsoft_iq_solution.py` |
| Remove entry point | `../../infra/scripts/remove_microsoft_iq_solution.py` |
| Fabric step modules | `../../infra/scripts/fabric/step_workspace_setup.py`, `step_workspace_admins.py`, `step_notebook_installer.py` |
| Foundry step modules | `../../infra/scripts/foundry/step_knowledge_base.py`, `step_agent_setup.py` |
| Cross-cutting helpers | `../../infra/scripts/common/config.py`, `logging_config.py`, `env_utils.py`, `env.py`, `pdf_utils.py`, `step_printer.py` |
| Fabric REST/Graph clients | `../../infra/scripts/fabric/fabric_api.py`, `graph_api.py` |
| Installer notebook | `../../infra/fabric/deploy/fabric_solution_installer.ipynb` |
| Workspace items (standard) | `../../src/fabric/fabric_workspace/` |
| Workspace items (ontology definitions) | `../../src/fabric/definitions/` |
| Bicep template / parameters | `../../infra/main.bicep`, `../../infra/main.parameters.json` |
| AZD config | `../../azure.yaml` |
| CI/CD workflow | `../../.github/workflows/azure-dev.yml` |

> **Common mistake** to avoid: the installer notebook lives at `infra/fabric/deploy/`, not `infra/deploy/`. Older versions of the manual guide had the wrong path — never write `../infra/deploy/fabric_solution_installer.ipynb`.

## Source of truth

| What | Authoritative source |
|---|---|
| Script entry-point names and step orchestration | [`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py), [`remove_microsoft_iq_solution.py`](../../infra/scripts/remove_microsoft_iq_solution.py) — never `install_fabric_solution.py` (renamed) |
| Fabric step behavior | Modules under [`infra/scripts/fabric/`](../../infra/scripts/fabric/) named `step_*.py` |
| Helper module APIs | [`infra/scripts/common/`](../../infra/scripts/common/) and [`infra/scripts/fabric/`](../../infra/scripts/fabric/) |
| Solution name and default workspace name | [`infra/scripts/common/config.py`](../../infra/scripts/common/config.py) — `SOLUTION_NAME = "Microsoft IQ"`, `default_workspace_name(suffix)` |
| Workspace items (standard) | Folder structure under [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/) |
| Workspace items (ontology) | Folder structure under [`src/fabric/definitions/`](../../src/fabric/definitions/) |
| Installer notebook configuration | First cell of [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) |
| Azure infrastructure (capacity, MI, Foundry resources) | [`infra/main.bicep`](../../infra/main.bicep) |
| azd hooks and orchestration | [`azure.yaml`](../../azure.yaml) |
| Fabric capacity SKU `@allowed(...)` list | [`infra/main.bicep`](../../infra/main.bicep) |

When these sources change, the deployment docs must be updated to match.

After modifying deployment docs, also check whether the related copilot instruction files need updating:

- [`.github/instructions/fabric-deployment-docs.instructions.md`](./fabric-deployment-docs.instructions.md) (this file) — section structure, relative paths, no-duplication rule.
- [`.github/instructions/deployment-guide.instructions.md`](./deployment-guide.instructions.md) — if the main guide structure also changes.
- [`.github/instructions/infra-scripts.instructions.md`](./infra-scripts.instructions.md) — if script references, env vars, or step ordering changed.
- [`.github/instructions/fabric-workspace.instructions.md`](./fabric-workspace.instructions.md) — if workspace item descriptions changed.
- [`.github/instructions/devcontainer.instructions.md`](./devcontainer.instructions.md) — if `.devcontainer/README.md` references either Fabric guide.
