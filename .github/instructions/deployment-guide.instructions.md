---
description: "Use when editing docs/DeploymentGuide.md, the top-level deployment guide for the Microsoft IQ Solution Accelerator. Covers document structure, script and resource references, relative link conventions, and source of truth."
applyTo: "docs/DeploymentGuide.md"
---

# Top-level deployment guide — structure and references

## Document

[`docs/DeploymentGuide.md`](../../docs/DeploymentGuide.md) is the **single end-to-end `azd up` guide** for the Microsoft IQ Solution Accelerator. It must stay short and self-contained. Operational Fabric-only details (manual portal-only flow) live in [`docs/fabric/DeploymentGuideFabricManual.md`](../../docs/fabric/DeploymentGuideFabricManual.md); the post-deployment Copilot Studio (Work IQ) configuration lives in [`docs/copilot/DeploymentGuide.md`](../../docs/copilot/DeploymentGuide.md). Keep the section structure below stable; only edit content within sections unless the deployment flow itself changes.

### Section structure

1. **Introduction** — one-paragraph summary of Fabric IQ + Microsoft Foundry components, followed by a **Table of Contents** sub-section (`### Table of Contents`) that links to every other top-level section (§2 *Deployment Environment Setup* through §8 *Additional Resources*) plus the relevant sub-sections of §5 (*Infrastructure Provisioned*, *Deployment Phases*) and §6 (*Azure Resources*, *Fabric IQ Components*, *Microsoft Foundry Components*, *Environment Variables*, *Next Steps*). Use GitHub-flavored markdown anchors (lowercase, hyphenated, no punctuation). The TOC must be kept in sync with the section headings whenever a section is added, removed, or renamed.
2. **Deployment Environment Setup** — four collapsible (`<details><summary>`) options that prepare the same prerequisites and converge on the common Deployment Commands. Order and wording must stay stable; only edit content within a `<details>` block:
   - *Option 1 · Local Deployment* — install `azd`, Python 3.9+, PowerShell 7+; clone the repo. Auth happens in Deployment Commands, not in this option.
   - *Option 2 · GitHub Codespaces* — launch via the **[Open in GitHub Codespaces badge](https://codespaces.new/microsoft/microsoft-iq-solution-accelerator)** at the top of the option (badge image: `https://github.com/codespaces/badge.svg`) **or** `Code → Codespaces`. The dev container's `postCreateCommand` provisions tooling automatically. Mention `azd auth login --use-device-code` as a fallback for the browser-redirect issue.
   - *Option 3 · Dev Container (VS Code + Docker Desktop)* — same image as Codespaces, run locally; `~/.azure` is bind-mounted from the host so a previous `azd auth login` carries over.
   - *Option 4 · GitHub Actions* — [`./.github/workflows/azure-dev.yml`](../../.github/workflows/azure-dev.yml) runs `azd up --no-prompt` via OIDC. Requires `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` secrets in the `miq-build` GitHub environment. This option **skips** the Deployment Commands section.
   Each option must link to [Deployment Commands](#deployment-commands) (except Option 4) and reference [`.devcontainer/README.md`](../../.devcontainer/README.md) for Options 2 & 3.
3. **Deployment Commands** — common path for Options 1–3. *Prerequisites* note ("complete one of the setup options above"); single bash code block in this order: `azd auth login` (commented "run only if not already logged in") → optional `azd env set GITHUB_TOKEN` → commented `azd env set AZURE_AI_DEPLOYMENTS_LOCATION` example noting the parameter is required and otherwise prompted → optional commented `azd env set` example overrides for defaulted parameters (e.g. `FABRIC_CAPACITY_SKU_NAME`) → `azd up` → optional `azd env get-values`. Followed by a blockquote linking to [Optional Configuration Variables](#optional-configuration-variables) for fine-grained tuning. Then a *Re-running Deployment* subsection covering idempotency.
4. **Post-Deployment Steps — Work IQ** — thin pointer section. One-paragraph framing that `azd up` covers Fabric IQ and Microsoft Foundry, and that Work IQ (Copilot Studio email-triggered agent) is the **manual** third component. Prominent link to [`docs/copilot/DeploymentGuide.md`](../../docs/copilot/DeploymentGuide.md) as the source of truth. A numbered 4-item summary mirroring the Copilot guide steps (Import solution → Configure connections → Configure email trigger → Publish agent + Teams channel). Connection list must mention the Foundry Agent endpoint comes from `AZURE_AI_AGENT_ENDPOINT` (`azd env get-values`). Mention the Power Platform solution lives at [`src/copilot/sln/MicrosoftIQAccelerator`](../../src/copilot/sln/MicrosoftIQAccelerator). End with a link to [`docs/copilot/README.md`](../../docs/copilot/README.md) for architecture overview and [`docs/copilot/TestingGuide.md`](../../docs/copilot/TestingGuide.md) for QA. **Do not duplicate** connection-by-connection details from the Copilot guide — keep this section as a pointer.
5. **Optional Configuration Variables** — single table of every `azd env set` variable that affects deployment behavior, plus the four "Available" lists (Fabric SKUs, AI deployment regions, use cases, deployment types). Must stay in sync with [`infra/main.parameters.json`](../../infra/main.parameters.json) and [`azure.yaml`](../../azure.yaml).
6. **Deployment Overview**
   - **Infrastructure Provisioned** — two subsections: Fabric IQ Resources and Microsoft Foundry Resources. Lists the resource types only, with [Microsoft Learn](https://learn.microsoft.com/) links.
   - **Deployment Phases** — single **table** with columns `# | Phase | Driver | Step / Resource | Description`. Phase 1 (Bicep) rows use `—` in the # column and group infra resources (capacity & MI; Foundry hub/project/connections; AI Search & Storage; OpenAI deployments). Phase 2 (Python) rows are numbered 1–6 and list the **6 steps** from `ALL_DEPLOYMENT_STEPS` (`setup_knowledge_base`, `setup_agent`, `setup_workspace`, `setup_administrators`, `upload_installer`, `run_installer`), each linking to its `step_*` module. The `setup_agent` row must call out **Best-effort** semantics in bold inside its Description cell.
7. **Deployment Results** — opens with a one-line summary that the deployment produces a single resource group plus the Fabric workspace.
   - **Azure Resources (Resource Group)** — table (`Component | Purpose`) covering Fabric Capacity, user-assigned Managed Identity, Microsoft Foundry Hub & Project, Azure OpenAI deployments, Azure AI Search, Azure Storage Account, Log Analytics + App Insights, and Foundry connections. Each row mentions the `{solution_suffix}` naming where applicable. Followed by a short **Access in the Azure portal** paragraph linking to [portal.azure.com](https://portal.azure.com), pointing at *Resource groups → `AZURE_RESOURCE_GROUP`*, and noting that diagnostic logs live under *Monitoring → Logs* on the Foundry / Search / Storage resources.
   - **Fabric IQ Components** — workspace tree (lakehouse name, notebook folders, semantic models, ontology, data agents). Must match items under [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/). Followed by an *Access your workspace* bullet list that points users to [app.fabric.microsoft.com](https://app.fabric.microsoft.com), the **Fabric Developer** experience switch, the default workspace name, and the direct-link template `https://app.fabric.microsoft.com/groups/{workspace_id}?experience=fabric-developer` (with `FABRIC_WORKSPACE_ID` from `azd env get-values`).
   - **Microsoft Foundry Components** — table (`Component | Default name | Purpose`) for Search Index `{solution_suffix}-documents`, Knowledge Source `{solution_suffix}-ks`, Knowledge Base `{solution_suffix}-kb`, KB MCP project connection `{solution_suffix}-kb-mcp-connection`, and Chat Agent `ChatAgent`. Followed by a *Verify in the Foundry portal* sub-section that opens with a one-line *how to access* note ([ai.azure.com](https://ai.azure.com), pick the hub then the project, with `AZURE_AI_PROJECT_NAME` / `AZURE_AI_AGENT_ENDPOINT` as references) and then the numbered checklist (Knowledge Bases → Agents → Connections), plus the [`infra/scripts/foundry/test_agent.py`](../../infra/scripts/foundry/test_agent.py) command.
   - **Environment Variables** — short list of key azd outputs (`AZURE_AI_AGENT_ENDPOINT`, `AZURE_AI_SEARCH_ENDPOINT`, `AZURE_STORAGE_BLOB_ENDPOINT`, `AZURE_FABRIC_CAPACITY_NAME`, `SOLUTION_NAME` / `SOLUTION_SUFFIX`).
   - **Next Steps** — add documents (re-run `azd up`), explore workspace, test agent (CLI or Foundry portal), view dashboards.
8. **Environment Cleanup** — `azd down` flow: predown hook ([`remove_microsoft_iq_solution.py`](../../infra/scripts/remove_microsoft_iq_solution.py)) → resource group deletion → `--purge` note.
9. **Additional Resources** — link to [`DeploymentGuideFabricManual.md`](../../docs/fabric/DeploymentGuideFabricManual.md), [`docs/copilot/DeploymentGuide.md`](../../docs/copilot/DeploymentGuide.md), [`docs/copilot/TestingGuide.md`](../../docs/copilot/TestingGuide.md), azd docs, Fabric docs, Foundry docs, GitHub repo.

### Style and scope

- **Keep it simple.** This is the entry-point guide. Do not duplicate deep content from [`docs/fabric/DeploymentGuideFabricManual.md`](../../docs/fabric/DeploymentGuideFabricManual.md) or [`docs/copilot/DeploymentGuide.md`](../../docs/copilot/DeploymentGuide.md); link to them instead.
- **`azd`-centric.** Every command is an `azd` command (or runs through it). Do not use `az login` or any other Azure CLI command in the Deployment Commands block — `azd auth login` is sufficient. Do not list Azure CLI as a required prerequisite under Option 1.
- **Do not list every helper module here.** Only the entry-point script and the 6 `step_*` modules should be linked from §6 Phase 2. Helper modules under [`infra/scripts/common/`](../../infra/scripts/common/) are an implementation detail.
- **Do not invent items.** Workspace components, env vars, step names, and Foundry resource names must be sourced from the files listed under "Source of truth" below. Resource defaults like `Microsoft IQ - {suffix}`, `{solution_suffix}-documents`, `{solution_suffix}-kb`, `{solution_suffix}-kb-mcp-connection`, and `ChatAgent` must match the values used in [`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py) and [`agent_api.py`](../../infra/scripts/foundry/agent_api.py).
- **No troubleshooting section.** Operational fixes belong in [`docs/fabric/DeploymentGuideFabricManual.md`](../../docs/fabric/DeploymentGuideFabricManual.md) (Troubleshooting table). The only exception is the *Verify in the Foundry portal* sub-section under §7, which doubles as the recovery path for `setup_agent`'s best-effort warning.
- **No repository-structure tree.** A repo file tree does not belong in this guide — it duplicates the workspace view and goes stale fast. Reference specific files inline instead.
- **Cross-document deduplication.** [`.devcontainer/README.md`](../../.devcontainer/README.md) must not duplicate the deployment commands or `azd env set` variable list. The dev container README is a configuration reference; this guide is the deployment walkthrough. When changes land, update the README pointer (Options 2 & 3) but never copy `azd up` instructions there.

## Relative path conventions

This doc lives at `docs/`. Relative paths from this location:

| Target | Relative path |
|---|---|
| Sibling guides | `./fabric/DeploymentGuideFabricManual.md`, `./copilot/DeploymentGuide.md`, `./copilot/TestingGuide.md`, `./copilot/README.md` |
| Install entry point | `../infra/scripts/install_microsoft_iq_solution.py` |
| Remove entry point | `../infra/scripts/remove_microsoft_iq_solution.py` |
| Step modules (only the 6 referenced in Phase 2) | `../infra/scripts/foundry/step_knowledge_base.py`, `step_agent_setup.py`<br>`../infra/scripts/fabric/step_workspace_setup.py`, `step_workspace_admins.py`, `step_notebook_installer.py` |
| Test script | `../infra/scripts/foundry/test_agent.py` |
| Installer notebook | `../infra/fabric/deploy/fabric_solution_installer.ipynb` |
| Workspace items | `../src/fabric/fabric_workspace/` |
| Foundry sample documents | `../src/foundry/data/documents/` |
| Copilot Studio solution package | `../src/copilot/sln/MicrosoftIQAccelerator` |
| Bicep template | `../infra/main.bicep` |
| Bicep parameters | `../infra/main.parameters.json` |
| AZD config | `../azure.yaml` |

## Source of truth

When any of these change, **update `docs/DeploymentGuide.md` to match**:

| What | Authoritative source | Sections to update |
|---|---|---|
| Deployment step order, names, behavior | `ALL_DEPLOYMENT_STEPS` and step bodies in [`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py) | §6 Phase 2 table rows |
| Step module file names | Files under [`infra/scripts/foundry/`](../../infra/scripts/foundry/) and [`infra/scripts/fabric/`](../../infra/scripts/fabric/) named `step_*.py` | §6 Phase 2 table links |
| Best-effort vs. abort semantics for a step | `_warn_step` vs. `_abort` calls in [`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py) | §6 Phase 2 Description column (add bold **Best-effort** note) |
| Dev container tooling, postCreate flow, Codespaces behavior | [`.devcontainer/devcontainer.json`](../../.devcontainer/devcontainer.json), [`post-create.sh`](../../.devcontainer/post-create.sh), [`setup_env.sh`](../../.devcontainer/setup_env.sh), [`.devcontainer/README.md`](../../.devcontainer/README.md) | §2 Options 2 & 3 |
| GitHub Actions workflow inputs/secrets/triggers | [`./.github/workflows/azure-dev.yml`](../../.github/workflows/azure-dev.yml) (`env:`, `secrets`, `paths:`, `environment:`) | §2 Option 4 |
| Codespaces deeplink owner/repo | Repository `<owner>/<repo>` (currently `microsoft/microsoft-iq-solution-accelerator`) | §2 Option 2 (badge URL `https://codespaces.new/microsoft/microsoft-iq-solution-accelerator`) |
| `azd` env vars and defaults | [`infra/main.parameters.json`](../../infra/main.parameters.json) (Bicep params) and [`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py) docstring (script-only vars) | §5 Optional Configuration Variables table + §3 inline `azd env set` example overrides |
| Fabric resource names (capacity, workspace, lakehouse) | [`infra/scripts/common/config.py`](../../infra/scripts/common/config.py) (`SOLUTION_NAME`, `default_workspace_name`) and the lakehouse folder name in [`src/fabric/fabric_workspace/lakehouses/`](../../src/fabric/fabric_workspace/lakehouses/) | §7 Azure Resources table + Fabric IQ Components workspace tree |
| Workspace items (notebooks, semantic models, ontology, data agents) | Folder structure under [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/) | §7 Fabric IQ Components workspace tree |
| Foundry resource naming (search index, KS, KB, MCP connection, agent) | `setup_knowledge_base` / `setup_agent` argument values built in [`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py); `CHAT_AGENT_NAME` constant in [`agent_api.py`](../../infra/scripts/foundry/agent_api.py) | §7 Microsoft Foundry Components table + *Verify in the Foundry portal* checklist |
| Available regions / SKUs / use cases | `@allowed(...)` lists in [`infra/main.bicep`](../../infra/main.bicep) | §5 (lists below the table) |
| Work IQ manual steps (Power Platform solution import, connections, email trigger, publish, Teams channel) | [`docs/copilot/DeploymentGuide.md`](../../docs/copilot/DeploymentGuide.md) | §4 Post-Deployment Steps — Work IQ (keep this section as a thin pointer; do not duplicate connection-by-connection details) |
| Cleanup behavior | [`remove_microsoft_iq_solution.py`](../../infra/scripts/remove_microsoft_iq_solution.py) and `predown` hook in [`azure.yaml`](../../azure.yaml) | §8 Environment Cleanup |

After modifying `docs/DeploymentGuide.md`, also check whether the related copilot instruction files need updating:

- [`.github/instructions/deployment-guide.instructions.md`](./deployment-guide.instructions.md) (this file) — section structure, relative paths, source-of-truth links
- [`.github/instructions/infra-scripts.instructions.md`](./infra-scripts.instructions.md) — if script references, env vars, or step ordering changed
- [`.github/instructions/fabric-workspace.instructions.md`](./fabric-workspace.instructions.md) — if workspace item descriptions changed
