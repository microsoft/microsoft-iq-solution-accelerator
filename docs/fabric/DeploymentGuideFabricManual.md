# Deployment Guide (Manual Option) for Microsoft IQ: Fabric IQ

This guide describes how to deploy the **Microsoft IQ: Fabric IQ** solution accelerator by importing and running the [fabric_solution_installer.ipynb](../infra/deploy/fabric_solution_installer.ipynb) notebook directly in a Microsoft Fabric workspace — no local tooling or scripts required.

## When to Use Manual Installation

- You prefer not to install `azd` or run local scripts
- You have an existing Fabric capacity and want a quick, portal-only deployment
- You're evaluating the solution with minimal setup

## Prerequisites

- **Microsoft Fabric capacity** must already exist (Fabric capacity or trial)
- **Fabric workspace** with capacity assigned
- **Workspace permissions** to create and manage Fabric items

## How to Install

### Step 1: Create a Fabric Workspace

1. Log in to [Microsoft Fabric](https://app.fabric.microsoft.com)
2. Click **Workspaces** → **+ New workspace**
3. Name your workspace (e.g., `Microsoft IQ`)
4. Assign a Fabric capacity or trial capacity
5. Click **Apply**

### Step 2: Download the Solution Installer Notebook

Download the [fabric_solution_installer.ipynb](../infra/deploy/fabric_solution_installer.ipynb) notebook to a local folder on your computer.

### Step 3: Import and Run the Solution Installer

1. In your Fabric workspace, click **+ New item** → **Import notebook**
2. Navigate to the folder where you saved [fabric_solution_installer.ipynb](../infra/deploy/fabric_solution_installer.ipynb)
3. Upload and open the **fabric_solution_installer** notebook
4. **(Optional)** If you want to deploy from a different branch, edit the `GITHUB_BRANCH` variable in the configuration cell (default: `"main"`)
5. Click **Run all** to execute the deployment

The installer notebook will:

- ✅ Install required Python packages
- ✅ Create the `miqsadata` lakehouse
- ✅ Deploy and configure all solution notebooks (23 notebooks)
- ✅ Upload sample data files across 6 business domains
- ✅ Deploy AI data agents and ontology semantic model
- ✅ Run post-deployment configuration tasks

---

## Deployment Verification

After the notebook completes, verify the following items exist in your workspace:

- **✅ Lakehouse**: `miqsadata` with tables across 6 business domains (customer, product, sales, finance, inventory, supplychain)
- **✅ Notebooks**: 23 notebooks organized in `data_management/`, `data_processing/`, `query_samples/`, `schema/`, and root pipeline notebooks
- **✅ Sample Data**: CSV files loaded in the lakehouse Files section
- **✅ Data Agents**: `data_agent_lakehouse` and `data_agent_ontology` for natural language querying
- **✅ Ontology**: `ontology_supplychain` providing a business-friendly semantic layer

All items are deployed from the [`fabric_workspace/`](../fabric_workspace/) folder in the repository.

---

## Troubleshooting

| Issue | Possible Cause | Resolution |
|-------|----------------|------------|
| Notebook import fails | File format unsupported | Ensure you downloaded the raw `.ipynb` file |
| Workspace capacity error | No capacity assigned | Assign a Fabric capacity or trial to the workspace |
| Installer notebook cell fails | Missing permissions or dependency | Review the failed cell output for details and re-run from that cell |
| Items not created | Notebook run incomplete | Confirm all cells completed; re-run any failed cells individually |

---

## Cleanup

To remove the deployed solution, delete the workspace from the Fabric portal:

1. Navigate to [Microsoft Fabric](https://app.fabric.microsoft.com)
2. Open **Workspace settings** for the installed workspace
3. Scroll to the bottom and select **Delete this workspace**

> ⚠️ **Important:** Deleting the workspace removes all contained items permanently.

---

## Next Steps

After successful deployment:

1. **Explore the workspace**: Review the deployed lakehouse, notebooks, data agents, and ontology model
2. **Customize for your needs**: Modify notebooks and data pipelines for your specific requirements
3. **Consider automation**: Use `azd up` for repeatable infrastructure provisioning alongside Fabric deployment — see [DeploymentGuideFabric.md](./DeploymentGuideFabric.md)

---

## Additional Resources

- [Microsoft Fabric Documentation](https://learn.microsoft.com/fabric/)
- [Fabric Workspace Management](https://learn.microsoft.com/fabric/admin/workspaces)
- [Main Deployment Guide (azd)](./DeploymentGuideFabric.md)

---

*This manual deployment guide is part of the Microsoft IQ: Fabric IQ solution accelerator. For the latest updates and documentation, visit the [official repository](https://github.com/microsoft/microsoft-iq-solution-accelerator).*