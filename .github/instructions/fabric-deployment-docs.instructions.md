---
description: "Use when editing deployment guides under docs/fabric/. Covers document structure, script and workspace references, relative link conventions, and source of truth for DeploymentGuideFabric.md and DeploymentGuideFabricManual.md."
applyTo: "docs/fabric/Deployment*.md"
---

# Deployment documentation — structure and references

## Documents

### DeploymentGuideFabric.md — Automated deployment (azd)

Main deployment guide. Section structure:

1. **Prerequisites** — tools (azd, az, python), Azure permissions ([RBAC](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles), [Microsoft.Fabric RP](https://learn.microsoft.com/azure/azure-resource-manager/management/azure-services-resource-providers)), API permissions ([Graph](https://learn.microsoft.com/graph/permissions-reference), [Fabric REST](https://learn.microsoft.com/rest/api/fabric/), [Power BI](https://learn.microsoft.com/rest/api/power-bi/))
2. **Deployment Overview** — two-phase: Phase 1 (Bicep → Azure resources), Phase 2 (Python → Fabric workspace). Includes: deployment architecture table with helper modules, [fabric-launcher](https://github.com/microsoft/fabric-launcher) workflow, idempotency notes
3. **Deployment Options** — 6 environments: local, Cloud Shell, Codespaces, VS Code Web, Dev Container, GitHub Actions
4. **Deployment Commands** — `azd up` quick-start
5. **Deployment Results** — Azure infrastructure + Fabric Components (workspace, folder structure, lakehouse, notebooks, data agents, ontology). Must match contents of [`fabric/fabric_workspace/`](../../fabric/fabric_workspace/)
6. **Advanced Configuration** — Infrastructure (Bicep params via [`main.bicep`](../../infra/main.bicep)), Workspace Settings, Admin Assignment, Optional Variables (`GITHUB_TOKEN`, `LOG_LEVEL`, `FABRIC_WORKSPACE_ID`), Python Environment
7. **Known Limitations** — Graph API lookup fallback, Fabric REST API permissions
8. **Environment Cleanup** — `azd down` process: predown hook runs [`remove_microsoft_iq_solution.py`](../../infra/scripts/remove_microsoft_iq_solution.py), then Azure resource removal
9. **Additional Resources** — external doc links

### DeploymentGuideFabricManual.md — Manual portal deployment

Simplified guide for importing [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) directly in [Microsoft Fabric](https://app.fabric.microsoft.com). Sections: When to Use, Prerequisites, 3-step install (create workspace → download notebook → import & run), Deployment Verification, Troubleshooting, Cleanup, Next Steps, Additional Resources.

## Relative path conventions

These docs live at `docs/fabric/`. Relative paths from this location:

| Target | Relative path |
|---|---|
| Other docs in same folder | `./DeploymentGuideFabricManual.md` |
| Install script | `../../infra/scripts/install_microsoft_iq_solution.py` |
| Remove script | `../../infra/scripts/remove_microsoft_iq_solution.py` |
| Helper modules | `../../infra/scripts/common/config.py`, `logging_config.py`, `env_utils.py`, `env.py`, `pdf_utils.py`, `step_printer.py`<br>`../../infra/scripts/fabric/step_workspace_setup.py`, `step_workspace_admins.py`, `step_notebook_installer.py`<br>`../../infra/scripts/foundry/step_knowledge_base.py`, `step_agent_setup.py` |
| Installer notebook | `../../infra/fabric/deploy/fabric_solution_installer.ipynb` |
| Workspace items | `../../src/fabric/fabric_workspace/`<br>`../../src/fabric/definitions/` |
| Bicep template | `../../infra/main.bicep` |
| AZD config | `../../azure.yaml` |
| CI/CD workflow | `../../.github/workflows/azure-dev.yml` |
| Bicep params | `../../infra/main.parameters.json` |

## Source of truth

| What | Authoritative source |
|---|---|
| Script behavior & env vars | Python files in [`infra/scripts/`](../../infra/scripts/) — entry points at `install_microsoft_iq_solution.py`, `remove_microsoft_iq_solution.py`; library packages at `common/`, `fabric/`, `foundry/` |
| Workspace items (standard items: lakehouse, notebooks, agents, reports, semantic models) | [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/) folder structure |
| Workspace items (ontology definitions) | [`src/fabric/definitions/`](../../src/fabric/definitions/) folder structure |
| Azure infrastructure | [`infra/main.bicep`](../../infra/main.bicep) |
| azd hooks & orchestration | [`azure.yaml`](../../azure.yaml) |
| Solution name & defaults | [`infra/scripts/common/config.py`](../../infra/scripts/common/config.py) |

When these sources change, the deployment docs must be updated to match.

After modifying deployment docs, also check whether the copilot instruction files need updating:
- [`.github/instructions/fabric-deployment-docs.instructions.md`](./fabric-deployment-docs.instructions.md) (this file) — section structure, relative paths
- [`.github/instructions/infra-scripts.instructions.md`](./infra-scripts.instructions.md) — if script references or env vars changed
- [`.github/instructions/fabric-workspace.instructions.md`](./fabric-workspace.instructions.md) — if workspace item descriptions changed
