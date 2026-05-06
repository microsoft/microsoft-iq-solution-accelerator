---
description: "Use when editing docs/DeploymentGuide.md, the top-level deployment guide for the Microsoft IQ Solution Accelerator. Covers document structure, script and resource references, relative link conventions, and source of truth."
applyTo: "docs/DeploymentGuide.md"
---

# Top-level deployment guide — structure and references

## Document

[`docs/DeploymentGuide.md`](../../docs/DeploymentGuide.md) is the **single end-to-end `azd up` guide** for the Microsoft IQ Solution Accelerator. It must stay short and self-contained — deeper Fabric-specific details belong in [`docs/fabric/DeploymentGuideFabric.md`](../../docs/fabric/DeploymentGuideFabric.md). Keep the section structure below stable; only edit content within sections unless the deployment flow itself changes.

### Section structure

1. **Introduction** — one-paragraph summary of Fabric IQ + Microsoft Foundry components.
2. **Deployment Overview**
   - **Infrastructure Provisioned** — two subsections: Fabric IQ Resources and Microsoft Foundry Resources. Lists the resource types only, with [Microsoft Learn](https://learn.microsoft.com/) links.
   - **Deployment Phases** — describes the **two-phase** workflow:
     - Phase 1 (Bicep) — `main.bicep` infra provisioning.
     - Phase 2 (Python) — orchestrated by [`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py); enumerates the **6 steps** from `ALL_DEPLOYMENT_STEPS` (`setup_knowledge_base`, `setup_agent`, `setup_workspace`, `setup_administrators`, `upload_installer`, `run_installer`), each linking to its `step_*` module. Calls out that `setup_agent` runs in **best-effort mode**.
3. **Deployment Commands** — Prerequisites (azd, Python), `Deploy Locally` block (clone → optional `GITHUB_TOKEN` → `azd auth login` → `azd up`), Re-running Deployment (idempotency).
4. **Optional Configuration Variables** — single table of every `azd env set` variable that affects deployment behavior. Must stay in sync with [`infra/main.parameters.json`](../../infra/main.parameters.json) and [`azure.yaml`](../../azure.yaml).
5. **Deployment Results**
   - **Fabric IQ Components** — workspace tree (lakehouse name, notebook folders, semantic models, ontology, data agents). Must match items under [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/).
   - **Microsoft Foundry Components** — search index, knowledge base, chat agent, and the [`infra/scripts/foundry/test_agent.py`](../../infra/scripts/foundry/test_agent.py) command.
   - **Environment Variables** — short list of key azd outputs.
   - **Next Steps** — add documents (re-run `azd up`), explore workspace, test agent, view dashboards.
6. **Environment Cleanup** — `azd down` flow: predown hook ([`remove_microsoft_iq_solution.py`](../../infra/scripts/remove_microsoft_iq_solution.py)) → resource group deletion → `--purge` note.
7. **Additional Resources** — link to [`DeploymentGuideFabric.md`](../../docs/fabric/DeploymentGuideFabric.md), azd docs, Fabric docs, Foundry docs, GitHub repo.

### Style and scope

- **Keep it simple.** This is the entry-point guide. Do not duplicate deep content from [`docs/fabric/DeploymentGuideFabric.md`](../../docs/fabric/DeploymentGuideFabric.md); link to it instead.
- **Do not list every helper module here.** Only the entry-point script and the 6 `step_*` modules should be linked from §2 Phase 2. Helper modules under [`infra/scripts/common/`](../../infra/scripts/common/) are an implementation detail covered by the Fabric guide.
- **Do not invent items.** Workspace components, env vars, and step names must be sourced from the files listed under "Source of truth" below.
- **No troubleshooting section.** Operational fixes belong in [`docs/fabric/DeploymentGuideFabric.md`](../../docs/fabric/DeploymentGuideFabric.md) §7 (Known Limitations) or [`docs/fabric/DeploymentGuideFabricManual.md`](../../docs/fabric/DeploymentGuideFabricManual.md).

## Relative path conventions

This doc lives at `docs/`. Relative paths from this location:

| Target | Relative path |
|---|---|
| Sibling guides | `./fabric/DeploymentGuideFabric.md`, `./fabric/DeploymentGuideFabricManual.md` |
| Install entry point | `../infra/scripts/install_microsoft_iq_solution.py` |
| Remove entry point | `../infra/scripts/remove_microsoft_iq_solution.py` |
| Step modules (only the 6 referenced in Phase 2) | `../infra/scripts/foundry/step_knowledge_base.py`, `step_agent_setup.py`<br>`../infra/scripts/fabric/step_workspace_setup.py`, `step_workspace_admins.py`, `step_notebook_installer.py` |
| Test script | `../infra/scripts/foundry/test_agent.py` |
| Installer notebook | `../infra/fabric/deploy/fabric_solution_installer.ipynb` |
| Workspace items | `../src/fabric/fabric_workspace/` |
| Foundry sample documents | `../src/foundry/data/documents/` |
| Bicep template | `../infra/main.bicep` |
| Bicep parameters | `../infra/main.parameters.json` |
| AZD config | `../azure.yaml` |

## Source of truth

When any of these change, **update `docs/DeploymentGuide.md` to match**:

| What | Authoritative source | Sections to update |
|---|---|---|
| Deployment step order, names, behavior | `ALL_DEPLOYMENT_STEPS` and step bodies in [`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py) | §2 Phase 2 list |
| Step module file names | Files under [`infra/scripts/foundry/`](../../infra/scripts/foundry/) and [`infra/scripts/fabric/`](../../infra/scripts/fabric/) named `step_*.py` | §2 Phase 2 links |
| Best-effort vs. abort semantics for a step | `_warn_step` vs. `_abort` calls in [`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py) | §2 Phase 2 (per-step note) |
| `azd` env vars and defaults | [`infra/main.parameters.json`](../../infra/main.parameters.json) (Bicep params) and [`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py) docstring (script-only vars) | §4 Optional Configuration Variables table |
| Fabric resource names (capacity, workspace, lakehouse) | [`infra/scripts/common/config.py`](../../infra/scripts/common/config.py) (`SOLUTION_NAME`, `default_workspace_name`) and the lakehouse folder name in [`src/fabric/fabric_workspace/lakehouses/`](../../src/fabric/fabric_workspace/lakehouses/) | §5 Fabric IQ Components workspace tree |
| Workspace items (notebooks, semantic models, ontology, data agents) | Folder structure under [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/) | §5 Fabric IQ Components workspace tree |
| Foundry resource naming (search index, KB, agent) | `setup_knowledge_base` / `setup_agent` argument values built in [`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py) | §5 Microsoft Foundry Components |
| Available regions / SKUs / use cases | `@allowed(...)` lists in [`infra/main.bicep`](../../infra/main.bicep) | §4 (lists below the table) |
| Cleanup behavior | [`remove_microsoft_iq_solution.py`](../../infra/scripts/remove_microsoft_iq_solution.py) and `predown` hook in [`azure.yaml`](../../azure.yaml) | §6 Environment Cleanup |

After modifying `docs/DeploymentGuide.md`, also check whether the related copilot instruction files need updating:

- [`.github/instructions/deployment-guide.instructions.md`](./deployment-guide.instructions.md) (this file) — section structure, relative paths, source-of-truth links
- [`.github/instructions/fabric-deployment-docs.instructions.md`](./fabric-deployment-docs.instructions.md) — if the Fabric-specific guide structure also changes
- [`.github/instructions/infra-scripts.instructions.md`](./infra-scripts.instructions.md) — if script references, env vars, or step ordering changed
- [`.github/instructions/fabric-workspace.instructions.md`](./fabric-workspace.instructions.md) — if workspace item descriptions changed
