# Deployment Guide for Microsoft IQ - Fabric IQ

Deploy the **Microsoft IQ** solution accelerator (Fabric IQ piece) using [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview) in minutes.

---

## Key Sections

| Section | Description |
|---------|-------------|
| [Prerequisites](#1-prerequisites) | Required permissions, tools, and setup |
| [Deployment Overview](#2-deployment-overview) | Overview of deployed resources and architecture |
| [Deployment Options](#3-deployment-options) | Local, cloud, and CI/CD deployment methods |
| [Deployment Commands](#4-deployment-commands) | One-command deployment instructions |
| [Deployment Results](#5-deployment-results) | Expected outcomes and verification steps |
| [Advanced Configuration Options](#6-advanced-configuration-options) | Optional customization parameters |
| [Known Limitations](#7-known-limitations) | Important constraints to review |
| [Environment Cleanup](#8-environment-cleanup) | How to remove deployed resources |
| [Additional Resources](#9-additional-resources) | Support and further reading |

### Alternative Deployment Methods

This guide focuses on automated deployment using Azure Developer CLI. For
manual deployment or existing Fabric capacity integration, refer to the
[Manual Deployment Guide](./DeploymentGuideFabricManual.md).

---

## 1. Prerequisites

To deploy this solution, ensure you have the following tools and permissions.

### Software Requirements

You need these tools installed to run the deployment commands.

| Tool | Version | Purpose | Download |
|------|---------|---------|----------|
| **Azure Developer CLI** | Latest | Orchestrates deployment | [Install azd](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) |
| **Azure CLI** | Latest | Admin tooling (optional) | [Install az](https://learn.microsoft.com/cli/azure/install-azure-cli) |
| **Python** | 3.9+ | Fabric configuration scripts | [Install Python](https://www.python.org/downloads/) |

> **💡 Tip**: You can skip installing tools by using [Azure Cloud Shell](https://shell.azure.com) or GitHub Codespaces.

### Permissions

Your deployment identity (User or Service Principal) requires the following permissions.

#### 🔐 Azure Permissions

- **Resource Group Access**: Ensure your deployment identity has permissions on target Resource Group to deploy Bicep templates and create Azure resources using appropriate [Azure RBAC built-in roles](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles) (e.g. has [Contributor](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#contributor) or [Owner](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#owner)) or appropriate [Azure RBAC custom role](https://learn.microsoft.com/azure/role-based-access-control/custom-roles) with necessary permissions
- **`Microsoft.Fabric` Resource Provider Access**: Verify your Azure Subscription has [Microsoft.Fabric resource provider](https://learn.microsoft.com/azure/azure-resource-manager/management/azure-services-resource-providers) enabled and your deployment identity has permissions on Resource Group to create [Microsoft Fabric capacity resource](https://learn.microsoft.com/azure/templates/microsoft.fabric/capacities?pivots=deployment-language-bicep)

#### 🔗 API Permissions

- **Microsoft Graph API - `User.Read`**: Delegated permission to read signed-in user profile information using [Microsoft Graph User permissions](https://learn.microsoft.com/graph/permissions-reference#user-permissions)
- **Microsoft Graph API - `openid`**: Delegated permission for sign in and user profile authentication using [OpenID Connect scopes](https://learn.microsoft.com/entra/identity-platform/scopes-oidc)
- **Fabric REST API - Workspace Management**: Access to create and manage Fabric workspaces for workspace structure deployment using [Fabric workspace APIs](https://learn.microsoft.com/rest/api/fabric/core/workspaces)
- **Fabric REST API - Item Creation**: Access to create lakehouses, notebooks, and reports for Fabric content deployment using [Fabric item APIs](https://learn.microsoft.com/rest/api/fabric/core/items)
- **Fabric REST API - Content Upload**: Access to upload files and manage workspace content for sample data and notebook deployment using [Fabric REST API scopes](https://learn.microsoft.com/rest/api/fabric/articles/scopes)
- **Power BI API - `Tenant.Read.All`**: Delegated permission to read organization's Power BI tenant information using [Power BI REST API permissions](https://learn.microsoft.com/rest/api/power-bi/#scopes)

<details>
<summary><strong>✅ Quick Check</strong> — Verify your tools are ready</summary>

```bash
# Check Azure Developer CLI
azd version

# Check Python
python --version
```

</details>

## 2. Deployment Overview

This solution accelerator uses a **two-phase deployment approach** to provision a complete data platform. The process is fully automated, idempotent, and safe to re-run.

### 1️⃣ Phase 1: Infrastructure (Azure)

*Powered by [Bicep](https://learn.microsoft.com/azure/azure-resource-manager/bicep/overview) & [Azure Resource Manager](https://learn.microsoft.com/azure/azure-resource-manager/management/overview)*
This phase creates the physical resources in your Azure subscription.

- **[Resource Group](https://learn.microsoft.com/azure/azure-resource-manager/management/manage-resource-groups-portal)**: A container for your resources.
- **[Fabric Capacity](https://learn.microsoft.com/fabric/enterprise/licenses)**: The compute engine (F SKU) that powers your data workloads.

### 2️⃣ Phase 2: Data Platform (Fabric)

*Powered by [Python](https://www.python.org/) & [Fabric REST APIs](https://learn.microsoft.com/rest/api/fabric/)*
This phase is orchestrated by [`install_fabric_solution.py`](../../infra/scripts/fabric/install_fabric_solution.py), which performs 4 Fabric bootstrap steps and then delegates the remaining solution setup to the installer notebook. Two Foundry steps run **before** the Fabric steps using environment variables sourced from `main.bicep` outputs (`AZURE_AI_SEARCH_ENDPOINT`, `AZURE_STORAGE_BLOB_ENDPOINT`, `AZURE_AI_AGENT_ENDPOINT`, `AI_SERVICE_NAME`, `AZURE_AI_PROJECT_NAME`):

- **Knowledge Base Setup**: Creates the Azure AI Search index, uploads PDFs from [`src/foundry/data`](../../src/foundry/data/), and provisions the Foundry IQ knowledge source and knowledge base (via [`foundry/step_knowledge_base.py`](../../infra/scripts/foundry/step_knowledge_base.py))
- **Agent Setup**: Creates an AI Foundry agent wired up to the Knowledge Base MCP tool (via [`foundry/step_agent_setup.py`](../../infra/scripts/foundry/step_agent_setup.py))

1. **Workspace Setup**: Creates or configures the [workspace](https://learn.microsoft.com/fabric/get-started/workspaces) and assigns it to the Fabric capacity (resumes paused capacities automatically)
2. **Workspace Administrators**: Adds administrators to the workspace (using [Graph API](https://learn.microsoft.com/graph/overview) resolution with fallback)
3. **Upload Installer Notebook**: Uploads [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) to the workspace (creates or updates if already exists). The notebook is automatically patched before upload to set `GITHUB_BRANCH` to the currently checked out git branch, ensuring the solution is deployed from the same branch you're working on
4. **Run Installer Notebook**: Executes [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) end-to-end inside Fabric. The notebook uses the [`fabric-launcher`](https://github.com/microsoft/fabric-launcher) library to pull the solution directly from GitHub and deploy all Fabric items leveraging [Fabric's Git integration and CI/CD capabilities](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration). The Fabric items are defined in two locations: standard items (lakehouses, notebooks, reports, semantic models, data agent) are in the [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/) folder structured to match the [Fabric workspace Git format](https://learn.microsoft.com/fabric/cicd/git-integration/git-get-started), while ontology definitions are in the [`src/fabric/definitions/`](../../src/fabric/definitions/) folder and deployed via custom post-deployment logic. The notebook then runs the following post-deployment tasks:
   - Run `pipeline_main` notebook: creates lakehouse tables from ingested CSV data
   - Deploy ontology items (`RetailSupplyChainOntologyModel`) with logical ID resolution and lakehouse SQL endpoint mapping
   - Deploy data agent items (`RetailSC Ontology Agent`)
   - Move installer notebook and ontologies to their target folders

#### Deployment Architecture

The Fabric deployment entry-point is [`install_fabric_solution.py`](../../infra/scripts/fabric/install_fabric_solution.py), which coordinates the bootstrap steps using a small set of helper modules:

| Helper Module | Purpose | Key Functions |
|---------------|---------|---------------|
| [`common/config.py`](../../infra/scripts/common/config.py) + [`common/env_utils.py`](../../infra/scripts/common/env_utils.py) + [`common/env.py`](../../infra/scripts/common/env.py) + [`common/logging_config.py`](../../infra/scripts/common/logging_config.py) + [`common/pdf_utils.py`](../../infra/scripts/common/pdf_utils.py) + [`common/step_printer.py`](../../infra/scripts/common/step_printer.py) | Cross-cutting helpers (azd, repo paths, env vars, file I/O, logging, PDF chunking, step formatting). Imported by both domain packages and the entry-point scripts. | `SOLUTION_NAME`, `REPO_ROOT`, `DATA_DIR`, `default_workspace_name()`, `get_required_env_var()`, `read_file_content()`, `parse_workspace_administrators()`, `load_all_env()`, `setup_logging()`, `process_pdfs_to_documents()`, `print_step()`, `print_steps_summary()` |
| [`fabric/step_workspace_setup.py`](../../infra/scripts/fabric/step_workspace_setup.py) | Workspace creation, capacity assignment, and auto-resume of paused capacities | `setup_workspace()` |
| [`fabric/step_workspace_admins.py`](../../infra/scripts/fabric/step_workspace_admins.py) | Administrator management with Graph API integration and fallback handling | `setup_workspace_administrators()` |
| [`fabric/step_notebook_installer.py`](../../infra/scripts/fabric/step_notebook_installer.py) | Installer notebook upload, in-memory patching (`GITHUB_BRANCH`, `GITHUB_TOKEN`), and Fabric job execution | `upload_installer_notebook()`, `run_installer_notebook()` |
| [`foundry/step_knowledge_base.py`](../../infra/scripts/foundry/step_knowledge_base.py) | Foundry IQ setup: AI Search index, knowledge source, knowledge base | `setup_knowledge_base()` |
| [`foundry/step_agent_setup.py`](../../infra/scripts/foundry/step_agent_setup.py) | Foundry IQ setup: AI Foundry agent + Knowledge Base MCP project connection | `setup_agent()` |

Fabric item definitions are organized in two locations:

- **[`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/)**: Contains standard items (lakehouses, notebooks, reports, semantic models, data agent) structured to match the [Fabric workspace Git format](https://learn.microsoft.com/fabric/cicd/git-integration/git-get-started), enabling [Fabric CI/CD](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration) deployment via the [`fabric-launcher`](https://github.com/microsoft/fabric-launcher) library
- **[`src/fabric/definitions/`](../../src/fabric/definitions/)**: Contains ontology definitions deployed via custom post-deployment logic using Fabric REST APIs

The installer notebook ([`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb)) is uploaded to the workspace and executed as a Fabric notebook job. It uses [`fabric-launcher`](https://github.com/microsoft/fabric-launcher) to download the repository from GitHub and deploy items from both folders into the Fabric workspace.

### 🔄 Idempotency & Re-runs

The deployment is designed to be **safe to re-run**. If you run `azd up` again:

- **Infrastructure**: Only updates settings if they have changed (e.g., [resizing Capacity](https://learn.microsoft.com/fabric/enterprise/scale-capacity)).
- **Workspace**: Detects existing workspace and skips creation.
- **Content**:
  - *Notebooks/Reports*: Updated to the latest version (overwrites changes).
  - *Data*: Preserved (sample data is re-uploaded if missing).
  - *Admins*: New admins are added; existing ones remain.

The deployment orchestration coordinates both phases, passing deployment parameters and ensuring proper sequencing. See [deployment options](#3-deployment-options) for different ways to run this deployment based on your preferred environment.

---

## 3. Deployment Options

Choose your deployment environment based on your workflow and requirements. All options use the same [Deployment commands](#4-deployment-commands) with environment-specific setup.

| Environment | Best For | Setup Required | Notes |
|-------------|----------|----------------|-------|
| **[Local Machine](#1-local-machine)** | Full development control | Install [software requirements](#software-requirements) | Most flexible, requires local setup |
| **[Azure Cloud Shell](#2-azure-cloud-shell)** | Zero setup | Just a web browser | Pre-configured tools, [session timeouts](https://learn.microsoft.com/azure/cloud-shell/limitations#system-state-and-persistence) |
| **[GitHub Codespaces](#3-github-codespaces)** | Team consistency | [GitHub account](https://github.com/signup) | [Cloud development environment](https://docs.github.com/en/codespaces/overview) |
| **[Visual Studio Code (WEB)](#4-visual-studio-code-web)** | Zero setup| Just a web browser | Web-based VS Code, session timeouts |
| **[Dev Container](#5-vs-code-dev-container)** | Standardized tooling | [Docker Desktop](https://www.docker.com/products/docker-desktop) + VS Code | [Containerized consistency](https://code.visualstudio.com/docs/devcontainers/containers) |
| **[GitHub Actions](#6-github-actions-cicd)** | Automated CI/CD | Service principal setup | Production deployments |

<details>
<summary><strong>1. Local Machine</strong></summary>

Deploy with full control over your development environment.

**Setup requirements**: Install the [software requirements](#software-requirements)

**Deployment**: Use the standard [Deployment commands](#4-deployment-commands)

</details>

<details>
<summary><strong>2. Azure Cloud Shell</strong></summary>

Deploy from Azure's browser-based terminal with zero local installation.

**Setup**: Open [Azure Cloud Shell](https://shell.azure.com) and install Azure Developer CLI:

```bash

curl -fsSL https://aka.ms/install-azd.sh | bash && exec bash
```

**Deployment**: Run the [Deployment commands](#4-deployment-commands) (azd pre-authenticated)

</details>

<details>
<summary><strong>3. GitHub Codespaces</strong></summary>

Deploy from a cloud development environment with pre-configured tools.

**Setup**:

1. Go to the [Microsoft IQ: Fabric IQ solution in GitHub Codespace](https://codespaces.new/microsoft/microsoft-iq-solution-accelerator?quickstart=1)
2. Follow the instructions on screen to create a new codespace with default setup.
3. Wait for the environment to initialize (2-3 minutes)
4. All tools are pre-installed; proceed to deployment

**Deployment**: Install azd and run [Deployment commands](#4-deployment-commands) with device authentication:

```bash
# Install azd if needed
curl -fsSL https://aka.ms/install-azd.sh | bash && exec bash

# Use device code authentication  
azd auth login --use-device-code

# Continue with deployment commands
```

</details>

<details>
<summary><strong>4. Visual Studio Code (WEB)</strong></summary>

Deploy from VS Code in the browser with zero local installation.

**Setup**:

1. Open the following link to launch VS Code Web:

    [![Open in Visual Studio Code Web](https://img.shields.io/static/v1?style=for-the-badge&label=Visual%20Studio%20Code%20(Web)&message=Open&color=blue&logo=visualstudiocode&logoColor=white)](https://vscode.dev/azure/?vscode-azure-exp=foundry&agentPayload=eyJiYXNlVXJsIjogImh0dHBzOi8vcmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbS9taWNyb3NvZnQvdW5pZmllZC1kYXRhLWZvdW5kYXRpb24td2l0aC1mYWJyaWMtc29sdXRpb24tYWNjZWxlcmF0b3IvcmVmcy9oZWFkcy9tYWluL2luZnJhL3ZzY29kZV93ZWIiLCAiaW5kZXhVcmwiOiAiL2luZGV4Lmpzb24iLCAidmFyaWFibGVzIjogeyJhZ2VudElkIjogIiIsICJjb25uZWN0aW9uU3RyaW5nIjogIiIsICJ0aHJlYWRJZCI6ICIiLCAidXNlck1lc3NhZ2UiOiAiIiwgInBsYXlncm91bmROYW1lIjogIiIsICJsb2NhdGlvbiI6ICIiLCAic3Vic2NyaXB0aW9uSWQiOiAiIiwgInJlc291cmNlSWQiOiAiIiwgInByb2plY3RSZXNvdXJjZUlkIjogIiIsICJlbmRwb2ludCI6ICIifSwgImNvZGVSb3V0ZSI6IFsiYWktcHJvamVjdHMtc2RrIiwgInB5dGhvbiIsICJkZWZhdWx0LWF6dXJlLWF1dGgiLCAiZW5kcG9pbnQiXX0=)
2. When prompted, sign in using your Microsoft account linked to your Azure subscription. 
   Select the appropriate subscription to continue.
3. Once the solution opens, the AI Foundry terminal will automatically start running the following command to install the required dependencies:

    ```bash
    sh install.sh
    ```

   During this process, you’ll be prompted with the message:

    ```text
    What would you like to do with these files?
    - Overwrite with versions from template
    - Keep my existing files unchanged
    ```

    Choose “**Overwrite with versions from template**” and provide a unique environment name when prompted.

**Deployment**: Install azd and run [Deployment commands](#4-deployment-commands) with device authentication:

```bash
# Install azd if needed
curl -fsSL https://aka.ms/install-azd.sh | bash && exec bash

# Use device code authentication  
azd auth login --use-device-code

# Continue with deployment commands
```

</details>

<details>
<summary><strong>5. VS Code Dev Container</strong></summary>

Deploy from a containerized environment for team consistency.

**Setup**:

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop) and [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Clone repository and open in VS Code
3. Reopen in container when prompted

**Deployment**: All tools pre-installed - run [Deployment commands](#4-deployment-commands) directly

</details>

<details>
<summary><strong>6. GitHub Actions (CI/CD)</strong></summary>

Automated deployment using the included [workflow](../../.github/workflows/azure-dev.yml).

**Setup**: Configure [repository variables](https://docs.github.com/en/actions/learn-github-actions/variables) and set up [service principal with federated credentials](https://learn.microsoft.com/azure/developer/github/connect-from-azure)

**Triggers**: Push to main branch or manual workflow dispatch

</details>

---

## 4. Deployment Commands

**One-command deployment** - Deploy everything with Azure Developer CLI ([prerequisites required](#1-prerequisites)):

```bash
# Clone and navigate to repository
git clone https://github.com/microsoft/microsoft-iq-solution-accelerator.git
cd microsoft-iq-solution-accelerator

# Authenticate (required)
azd auth login

# Optional: Customize deployment (see Advanced Configuration Options below)
azd env set FABRIC_WORKSPACE_NAME "My IQ Platform"
azd env set AZURE_LOCATION "westeurope"
azd env set FABRIC_CAPACITY_SKU_NAME "F8"  # Optional: defaults to F2
azd env set GITHUB_TOKEN "ghp_xxxxxxxxxxxx"  # Only needed for private repositories

# Deploy everything
azd up
```

> **💡 Configuration Tip**: You can customize the deployment with optional infrastructure variables like `FABRIC_CAPACITY_SKU_NAME`, `AZURE_LOCATION`, or workspace variables like `FABRIC_WORKSPACE_NAME`, `LOG_LEVEL`, and `GITHUB_TOKEN` before running `azd up`. See [Advanced Configuration Options](#6-advanced-configuration-options) for details.

> **⚠️ Known Deployment Issue - Notebook Session Timeouts**
> 
> During deployment, the installer notebook may occasionally fail with timeout errors. Common error messages include:
> 
> **Spark Session Timeout:**
> ```
> SparkCoreError/Other: Livy session has failed. Error code: SparkCoreError/Other.
> SessionInfo.State from SparkCore is Error: Error while trying to establish a connection
> through the managed network. ErrorCode GetManagedVnetTimeout. Please retry.
> ```
> 
> **Notebook Execution Timeout:**
> ```
> Exception while executing run_installer: Installer notebook finished with status 'Timeout'. 
> Error: Operation 'Run notebook 'fabric_solution_installer' (ID: d0eb206f-885d-4592-bab2-b3f4af9c1711)' 
> timed out after 60m 0s
> ```
> 
> **Root Cause**: These are transient platform issues caused by intermittent delays during [Spark session](https://learn.microsoft.com/fabric/data-engineering/spark-job-definition) provisioning, notebook execution, or managed virtual network connectivity. These issues are not configuration-specific and can occur across different regions and capacities.
> 
> **Workaround**: Simply re-run the deployment command (`azd up`). The deployment is idempotent and will resume from where it stopped. Timeout failures typically succeed on subsequent retry attempts.

During deployment, you'll specify:

- **Environment name** (e.g., "miq-dev"). This will be used to build the name of the deployed Azure resources.
- **Azure subscription**.
- **Azure resource group**.

**What you get**: Complete [medallion architecture](https://learn.microsoft.com/azure/databricks/lakehouse/medallion) with Fabric capacity, [lakehouses](https://learn.microsoft.com/fabric/data-engineering/lakehouse-overview) (Bronze/Silver/Gold), [notebooks](https://learn.microsoft.com/fabric/data-engineering/how-to-use-notebook), sample data, and [Power BI reports](https://learn.microsoft.com/power-bi/create-reports/service-report-create-new).

> **💡 Alternative Deployment Option**
> This guide uses Azure Developer CLI for automated deployment. If you prefer more granular control or have an existing Fabric capacity, see the [Manual Deployment Guide](./DeploymentGuideFabricManual.md).

### Next Steps

- **First deployment**: Follow the commands above - they work in [multiple environments](#3-deployment-options)
- **Need different setup**: See [deployment environment options](#3-deployment-options) (Cloud Shell, Codespaces, etc.)
- **Understand the process**: Review [deployment overview](#2-deployment-overview) for technical details
- **See what's created**: Check [deployment results](#5-deployment-results) for detailed component overview with screenshots
- **Want to customize**: Explore [configuration options](#6-advanced-configuration-options) for naming, capacity sizing, and admin setup
- **Limitations**: Review [known limitations](#7-known-limitations) for common issues and workarounds
- **Remove environment**: Use [environment cleanup](#8-environment-cleanup) to completely remove your deployment

---

## 5. Deployment Results

After successful deployment, you'll have a complete data platform implementing medallion architecture.

### Azure Infrastructure

| Resource | Purpose |
|----------|---------|
| **[Fabric Capacity](https://learn.microsoft.com/fabric/admin/capacity-settings?tabs=power-bi-premium)** | Dedicated compute for Fabric workloads |

![Screenshot of deployed Azure resources](../images/deployment/azure-resources.png)

### Fabric Components

Fabric items are defined in the [`src/fabric/fabric_workspace/`](../../src/fabric/fabric_workspace/) folder (standard items) and [`src/fabric/definitions/`](../../src/fabric/definitions/) folder (ontology definitions), and deployed via the [`fabric-launcher`](https://github.com/microsoft/fabric-launcher) library using [Fabric's CI/CD import capabilities](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration) plus custom ontology deployment logic. Deployment is staged: lakehouses first, then notebooks, then ontology and data agents via post-deployment tasks, ensuring correct dependency order. Re-running the installer notebook updates existing items in-place.

#### Fabric Workspace

Workspace created with the specified or default name (e.g., `Microsoft IQ - {suffix}`).

![Screenshot of resulting Fabric workspace](../images/deployment/fabric-workspace.png)

#### Folder Structure

```text
your-workspace/
├── data_agent/               # AI Data Agent (natural language query)
│   └── RetailSC Ontology Agent/
├── dashboards/               # Power BI Reports & Semantic Models
│   ├── Sales Overview/       # Report + Semantic Model
│   └── Supply Chain Management/  # Report + Semantic Model
├── lakehouses/               # Fabric lakehouse
│   └── miqsadata/
├── notebooks/                # Data pipelines & utilities (26 notebooks)
│   ├── data_management/      # Table operations (create, drop, load, truncate)
│   ├── data_processing/      # Domain data loaders (customer, finance, inventory, product, sales, supplychain, shared)
│   ├── query_samples/        # Ad-hoc queries (data summary, schema lists, order counts)
│   ├── schema/               # Schema models (customer, finance, inventory, product, sales, supplychain, shared)
│   └── (root)/               # Pipeline orchestration (pipeline_main, pipeline_update, reset_or_debug, sampe_data_query)
└── ontology/                 # Ontology & Semantic Model
    ├── RetailSupplyChainOntologyModel/
    └── RetailSupplyChainModel/  # Semantic Model
```

#### Lakehouse

The solution deploys a single [lakehouse](https://learn.microsoft.com/fabric/data-engineering/lakehouse-overview) that serves as the data store:

| Name | Purpose |
|------|---------|
| `miqsadata` | Data lakehouse with schema-on-read tables across 6 business domains |

The lakehouse is configured with [shortcut](https://learn.microsoft.com/fabric/onelake/onelake-shortcuts-overview) support for external data sources (OneLake, ADLS Gen2, Dataverse, Amazon S3, Google Cloud Storage, Azure Blob Storage, OneDrive/SharePoint).

![Screenshot of resulting Fabric lakehouses](../images/deployment/fabric-lakehouse.png)

#### Data & Schema

The lakehouse manages 25 tables across 6 business domains plus a shared date dimension:

- **Customer** (5 tables): Customer, CustomerTradeName, CustomerRelationshipType, Location, CustomerAccount
- **Product** (3 tables): ProductLine, Product, ProductCategory
- **Sales** (3 tables): Order, OrderLine, OrderPayment
- **Finance** (3 tables): invoice, account, payment
- **Inventory** (6 tables): Warehouses, Inventory, InventoryTransactions, PurchaseOrders, PurchaseOrderItems, DemandForecast
- **Supply chain** (4 tables): Suppliers, ProductSuppliers, SupplyChainEvents, SupplyChainEventImpacts
- **Shared** (1 table): DimDate

Sample data is uploaded into the lakehouse during deployment to enable immediate exploration.

#### Notebooks

**26 [notebooks](https://learn.microsoft.com/fabric/data-engineering/how-to-use-notebook)** organized by function:

| Folder | Count | Purpose |
|--------|-------|---------|
| **data_management/** | 4 | Table lifecycle operations: `create_scheme_tables`, `drop_all_tables`, `load_data_all_tables`, `truncate_all_tables` |
| **data_processing/** | 7 | Domain data loaders: `load_customer`, `load_finance`, `load_inventory`, `load_product`, `load_sales`, `load_supplychain`, `load_shared` |
| **query_samples/** | 4 | Ad-hoc queries: `get_data_summary`, `list_schema_tables`, `order_counts`, `sql_order_counts` (SQL) |
| **schema/** | 7 | Schema model definitions: `model_customer`, `model_finance`, `model_inventory`, `model_product`, `model_sales`, `model_supplychain`, `model_shared` |
| *(root)* | 4 | Pipeline orchestration: `pipeline_main`, `pipeline_update`, `reset_or_debug`, `sampe_data_query` |

![Screenshot of resulting Fabric notebooks](../images/deployment/fabric-notebooks.png)

#### AI Data Agents

One [Fabric Data Agent](https://learn.microsoft.com/fabric/data-science/ai-agents-overview) is deployed for natural language interaction with the data:

| Agent | Purpose |
|-------|---------|
| `RetailSC Ontology Agent` | Query data through the ontology semantic model using natural language. Based on the Semantic Model → Ontology → Data Agent approach with comprehensive AI instructions |


> **Note**: The solution supports additional data agent approaches (lakehouse-based, entity model-based) that can be manually configured. See [fabric_data_agent/README.md](./fabric_data_agent/README.md) for details.

#### Ontology & Semantic Models

| Item | Type | Purpose |
|------|------|---------|
| `RetailSupplyChainOntologyModel` | [Ontology](https://learn.microsoft.com/fabric/data-science/ontology) | Ontology-based model providing a business-friendly view of the lakehouse data |
| `RetailSupplyChainModel` | [Semantic Model](https://learn.microsoft.com/power-bi/connect-data/service-datasets-understand) | Semantic model based on lakehouse schema used to generate the ontology |

![Screenshot of Ontology](../images/deployment/fabric-ontology.png)

#### Dashboards & Semantic Models

| Item | Type | Purpose |
|------|------|---------|
| `Sales Overview` | Semantic Model + [Report](https://learn.microsoft.com/power-bi/create-reports/service-report-create-new) | [Power BI](https://learn.microsoft.com/power-bi/fundamentals/power-bi-overview) semantic model and report for sales analytics |
| `Supply Chain Management` | Semantic Model + Report | Power BI semantic model and report for supply chain analytics |

---

## 6. Advanced Configuration Options

The solution accelerator provides flexible configuration options to customize your deployment. Parameters can be configured through **Azure Developer CLI environment variables** (`azd env set`) for local deployments or through **GitHub repository variables** for CI/CD deployments.

> **📁 Configuration Files Reference:**
>
> - Infrastructure: [`infra/main.bicep`](../../infra/main.bicep) - Azure resource definitions
> - Deployment orchestration: [`azure.yaml`](../../azure.yaml) - AZD project configuration  
> - CI/CD workflow: [`.github/workflows/azure-dev.yml`](../../.github/workflows/azure-dev.yml) - GitHub Actions pipeline
> - Fabric deployment: [`infra/scripts/fabric/install_fabric_solution.py`](../../infra/scripts/fabric/install_fabric_solution.py) - Fabric solution bootstrap orchestrator
> - Installer notebook: [`infra/fabric/deploy/fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) - Full solution deployment notebook
> - Helper modules: [`infra/scripts/common/`](../../infra/scripts/common/), [`infra/scripts/fabric/`](../../infra/scripts/fabric/), and [`infra/scripts/foundry/`](../../infra/scripts/foundry/) - Bootstrap helper functions

### 🏗️ Infrastructure Configuration

Configure the Azure infrastructure components through Bicep template parameters defined in [`main.bicep`](../../infra/main.bicep).

<details>
<summary><strong>Azure Resources</strong></summary>

| Parameter | AZD Environment Variable | GitHub Actions Variable | Description | Default | Example |
|-----------|-------------------------|------------------------|-------------|---------|---------|
| **Solution Name** | `solutionName` | `AZURE_ENV_NAME` | Friendly name for the application/solution (3-20 chars) | `udfwfsa` | `mycompany-iq` |
| **Location** | `AZURE_LOCATION` | `AZURE_LOCATION` | Azure region for resource deployment | Resource group location | `eastus`, `westus2`, `westeurope` |
| **Existing Fabric Capacity** *(Optional)* | `AZURE_EXISTING_FABRIC_CAPACITY_NAME` | `AZURE_EXISTING_FABRIC_CAPACITY_NAME` | Name of an existing Fabric capacity to use. If provided, skips capacity creation and uses the specified capacity instead | Empty (creates new capacity) | `fc-mycompany-prod` |
| **Fabric Capacity SKU** *(Optional)* | `FABRIC_CAPACITY_SKU_NAME` | `FABRIC_CAPACITY_SKU_NAME` | Fabric capacity tier and performance level (only applies when creating new capacity) | `F2` | `F4`, `F8`, `F16`, `F32`, `F64`, `F128`, `F256`, `F512`, `F1024`, `F2048` |
| **Enable Telemetry** | `enableTelemetry` | Not directly supported* | Enable/disable usage telemetry collection | `true` | `false` |

*GitHub Actions can use additional parameters through Bicep parameter files or workflow modifications.*

**Configuration Examples:**

<details>
<summary><strong>🖥️ Azure Developer CLI</strong></summary>

```bash
# Set environment variables (used by main.parameters.json)
azd env set AZURE_LOCATION "westeurope"
azd env set FABRIC_CAPACITY_SKU_NAME "F8"

# Optional: Use an existing Fabric capacity instead of creating a new one
azd env set AZURE_EXISTING_FABRIC_CAPACITY_NAME "fc-mycompany-prod"

azd up
```

</details>

<details>
<summary><strong>🚀 GitHub Actions</strong></summary>

Set as a repository variable or modify [`azure-dev.yml`](../../.github/workflows/azure-dev.yml) to add environment variables:

```yaml
- name: Deploy using azd up and Run Fabric provisioning script
  env:
    FABRIC_CAPACITY_SKU_NAME: "F8"
    AZURE_LOCATION: ${{ env.AZURE_LOCATION }}
  run: |
    azd env new $ENV_NAME --no-prompt
    azd env set FABRIC_CAPACITY_SKU_NAME "$FABRIC_CAPACITY_SKU_NAME"
    azd up --no-prompt
```

Alternatively, set it as a [GitHub repository variable](https://docs.github.com/en/actions/learn-github-actions/variables) named `FABRIC_CAPACITY_SKU_NAME` and reference it in the workflow with `${{ vars.FABRIC_CAPACITY_SKU_NAME }}`.

</details>

**Fabric Capacity SKU Selection Guide:**

> **Note:** SKU selection only applies when creating a new Fabric capacity. If you specify `AZURE_EXISTING_FABRIC_CAPACITY_NAME`, the SKU setting is ignored.

- **F2-F4**: Development and testing environments
- **F8-F32**: Small to medium production workloads
- **F64-F256**: Large enterprise production workloads  
- **F512-F2048**: High-performance analytics and data science workloads

For detailed capacity planning, see [Fabric capacity planning](https://learn.microsoft.com/fabric/admin/capacity-planning).

</details>

### 🏢 Fabric Workspace Configuration

Customize the Fabric workspace setup and naming conventions. These parameters are used by the [`install_fabric_solution.py`](../../infra/scripts/fabric/install_fabric_solution.py) script during post-provisioning.

> **⚠️ Important**: Variables marked as "Bicep output" (like `AZURE_FABRIC_CAPACITY_NAME`, `SOLUTION_SUFFIX`, `AZURE_FABRIC_CAPACITY_ADMINISTRATORS`) are automatically set by the deployment process and should **NOT** be manually configured. These are outputs from [`main.bicep`](../../infra/main.bicep) and will be populated after infrastructure deployment.

<details>
<summary><strong>Workspace Settings</strong></summary>

| Parameter | AZD Environment Variable | GitHub Actions Variable | Description | Default | Example |
|-----------|-------------------------|------------------------|-------------|---------|---------|
| **Capacity Name** | `AZURE_FABRIC_CAPACITY_NAME` | Bicep output (auto-set) | Microsoft Fabric capacity name - **DO NOT SET MANUALLY** (automatically populated from Bicep deployment) | Generated from Bicep | `fc-miq-abc123` |
| **Subscription ID** | `AZURE_SUBSCRIPTION_ID` | Bicep output (auto-set) | Azure subscription ID containing the Fabric capacity - **DO NOT SET MANUALLY** (automatically populated by `azd`) | Set by `azd` | `ff9b5430-90ea-...` |
| **Resource Group** | `AZURE_RESOURCE_GROUP` | Bicep output (auto-set) | Resource group containing the Fabric capacity - **DO NOT SET MANUALLY** (automatically populated by `azd`). Required to auto-resume paused capacities | Set by `azd` | `rg-miq-dev` |
| **Solution Suffix** | `SOLUTION_SUFFIX` | Bicep output (auto-set) | Unique suffix for resource naming - **DO NOT SET MANUALLY** (automatically populated from Bicep deployment) | Generated from Bicep | `miqabc12` |
| **Workspace Name** | `FABRIC_WORKSPACE_NAME` | `FABRIC_WORKSPACE_NAME` | Custom name for the Fabric workspace | `Microsoft IQ - {solution_suffix}` | `"MyCompany Data Foundation"`, `"Analytics Platform - DEV"` |

**Configuration Examples:**

<details>
<summary><strong>🖥️ Azure Developer CLI</strong></summary>

```bash
azd env set FABRIC_WORKSPACE_NAME "Analytics Platform - DEV"
azd up
```

</details>

<details>
<summary><strong>🚀 GitHub Actions</strong></summary>

Modify [`azure-dev.yml`](../../.github/workflows/azure-dev.yml) environment variables:

```yaml
env:
  FABRIC_WORKSPACE_NAME: "Analytics Platform (dev)"
```

</details>

**Workspace Naming Best Practices:**

- Use descriptive names that indicate purpose and environment
- Consider organizational naming conventions
- Include environment indicators for multi-environment deployments (Dev, Test, Prod)
- Avoid special characters that might cause conflicts with Fabric APIs

</details>

### 👥 Fabric Workspace Administrator Configuration

Manage workspace administrators and security permissions for the Fabric workspace. These parameters are processed by both the Bicep template ([`main.bicep`](../../infra/main.bicep)) for capacity-level admins and the Fabric deployment script ([`install_fabric_solution.py`](../../infra/scripts/fabric/install_fabric_solution.py)) for workspace-level admins.

<details>
<summary><strong>Admin Assignment Options</strong></summary>

| Parameter | AZD Environment Variable | GitHub Actions Support | Description | Format | Example |
|-----------|-------------------------|------------------------|-------------|--------|---------|
| **Capacity Administrators** | `AZURE_FABRIC_CAPACITY_ADMINISTRATORS` | Bicep output (auto-set) | **DO NOT SET MANUALLY** - Automatically populated from Bicep deployment with capacity-level administrators | JSON array (read-only) | `["user1@contoso.com", "12345678-1234-1234-1234-123456789012"]` |
| **Workspace Administrators** | `FABRIC_WORKSPACE_ADMINISTRATORS` | Via environment variables | Comma-separated list of workspace-level administrator identities. Accepts **User Principal Names (UPNs)** like `user@domain.com` OR **Azure Entra ID Object IDs (GUIDs)** obtained from Azure portal | Comma-separated string | `"user@contoso.com, admin@contoso.com"` OR `"87654321-4321-4321-4321-210987654321, 12345678-1234-1234-1234-123456789012"` |

*GitHub Actions workflow uses Bicep output for admin configuration. See examples below for customization.*

**Administrator Identity Formats:**

`FABRIC_WORKSPACE_ADMINISTRATORS` accepts flexible identity formats:

- **User Principal Names (UPNs)**: `user@domain.com` format for individual users (requires Graph API permissions to resolve)
- **Azure Entra ID Object IDs (GUIDs)**: `12345678-1234-1234-1234-123456789012` format - recommended when Graph API permissions are unavailable
  - Get user object IDs: `az ad user show --id user@contoso.com --query id -o tsv`
  - Get service principal object IDs: `az ad sp show --id <app-id> --query id -o tsv`
- **Mixed Format**: Combine UPNs and GUIDs in the same comma-separated list

**Configuration Examples:**

<details>
<summary><strong>🖥️ Azure Developer CLI</strong></summary>

```bash
# NOTE: Do NOT manually set AZURE_FABRIC_CAPACITY_ADMINISTRATORS - it's automatically set by Bicep deployment

# Option 1: Set workspace administrators using UPNs (requires Graph API permissions)
azd env set FABRIC_WORKSPACE_ADMINISTRATORS "user@contoso.com, admin@contoso.com"

# Option 2: Set workspace administrators using Azure Entra ID Object IDs (recommended when Graph API unavailable)
azd env set FABRIC_WORKSPACE_ADMINISTRATORS "87654321-4321-4321-4321-210987654321, 12345678-1234-1234-1234-123456789012"

# Option 3: Mix UPNs and Object IDs
azd env set FABRIC_WORKSPACE_ADMINISTRATORS "user@contoso.com, 12345678-1234-1234-1234-123456789012"

azd up
```

</details>

<details>
<summary><strong>🚀 GitHub Actions</strong></summary>

**Option A**: Update [`main.parameters.json`](../../infra/main.parameters.json):

```json
{
  "parameters": {
    "solutionName": { "value": "${AZURE_ENV_NAME}" },
    "fabricAdminMembers": { "value": ["user@contoso.com"] }
  }
}
```

**Option B**: Override in workflow [`azure-dev.yml`](../../.github/workflows/azure-dev.yml):

```yaml
- name: Deploy Infrastructure  
  uses: azure/bicep-deploy@v2
  with:
    parameters: |
      {
        "fabricAdminMembers": ["user@contoso.com", "sp-guid"]
      }
```

</details>

**Administrator Assignment Behavior:**

- **Automatic Default Admin**: The deployment identity (user or service principal) is automatically added as a Fabric capacity admin
- **Duplicate Detection**: Prevents adding the same principal multiple times
- **Fallback Logic**: Object ID method tries both User and ServicePrincipal types automatically
- **Graph API Resolution**: UPN method uses Microsoft Graph API for identity resolution

**Permission Requirements:**
Administrators configured through these parameters will have **Admin** role on the Fabric workspace, providing:

- Full workspace management capabilities
- Ability to manage workspace items (lakehouses, notebooks, reports)
- User and permission management within the workspace
- Workspace settings configuration

</details>

### � Additional Optional Configuration

These optional environment variables control advanced deployment behavior in [`install_fabric_solution.py`](../../infra/scripts/fabric/install_fabric_solution.py) and [`remove_fabric_solution.py`](../../infra/scripts/fabric/remove_fabric_solution.py).

<details>
<summary><strong>Optional Variables</strong></summary>

| Parameter | AZD Environment Variable | Description | Default | Example |
|-----------|-------------------------|-------------|---------|---------|
| **Azure Location** | `AZURE_LOCATION` | Azure region for resource deployment. When not set, uses the location of the selected resource group | Resource group location | `eastus`, `westus2`, `westeurope`, `northeurope` |
| **GitHub Token** | `GITHUB_TOKEN` | GitHub personal access token. When set, the installer notebook is patched to include the token for private repository access. Only needed when deploying from a private fork | Not set | `ghp_xxxxxxxxxxxx` |
| **Log Level** | `LOG_LEVEL` | Controls verbosity of deployment script logging. Set to `DEBUG` for detailed HTTP request/response tracing | `INFO` | `DEBUG`, `WARNING` |
| **Workspace ID** | `FABRIC_WORKSPACE_ID` | Target an existing workspace by ID during removal (used by `remove_fabric_solution.py`). If both `FABRIC_WORKSPACE_NAME` and `FABRIC_WORKSPACE_ID` are set, the name takes precedence | Not set | `12345678-1234-...` |

**Configuration Examples:**

```bash
# Set Azure region (optional - defaults to resource group location)
azd env set AZURE_LOCATION "westeurope"

# Enable debug logging for troubleshooting
azd env set LOG_LEVEL DEBUG

# Set GitHub token for private repo access
azd env set GITHUB_TOKEN "ghp_xxxxxxxxxxxx"

azd up
```

</details>

### �🐍 Python Environment Configuration Options

Configure deployment behavior and troubleshooting options. These parameters are handled by the PowerShell orchestration script ([`Run-PythonScript.ps1`](../../infra/scripts/utils/Run-PythonScript.ps1)).

<details>
<summary><strong>Deployment Customization</strong></summary>

These options are primarily used for configuring the appropriate environment for each deployment process based on elements such as underlying operating system or specialized environments such as containerized deployments or GitHub-hosted runners.

| Parameter | PowerShell Switch | AZD Support | GitHub Actions Support | Description | Use Case |
|-----------|-------------------|-------------|------------------------|-------------|----------|
| **Skip Virtual Environment** | `-SkipPythonVirtualEnvironment` | Manual override | ✅ Used in workflow | Use system Python instead of virtual environment | System-wide Python management, containerized environments |
| **Skip Dependencies** | `-SkipPythonDependencies` | Manual override | ✅ Used in workflow | Skip installing Python packages (assume pre-installed) | Pre-configured environments, repeated deployments |
| **Skip Pip Upgrade** | `-SkipPipUpgrade` | Manual override | ✅ Used in workflow | Skip upgrading pip to latest version | Environments with controlled pip versions |

**Configuration Examples:**

<details>
<summary><strong>🖥️ Azure Developer CLI</strong></summary>

These parameters are automatically optimized in [`azure.yaml`](../../azure.yaml):

```yaml
hooks:
  postprovision:
    windows:
      shell: pwsh
      run: ./fabric/infra/scripts/utils/Run-PythonScript.ps1 -ScriptPath "fabric/infra/scripts/fabric/install_fabric_solution.py"
      interactive: true
      continueOnError: false
    posix:
      shell: pwsh
      run: ./fabric/infra/scripts/utils/Run-PythonScript.ps1 -ScriptPath "fabric/infra/scripts/fabric/install_fabric_solution.py" -SkipPythonVirtualEnvironment
      interactive: true
      continueOnError: false
  predown:
    windows:
      shell: pwsh
      run: ./fabric/infra/scripts/utils/Run-PythonScript.ps1 -ScriptPath "fabric/infra/scripts/fabric/remove_fabric_solution.py"
      interactive: true
      continueOnError: false
    posix:
      shell: pwsh
      run: ./fabric/infra/scripts/utils/Run-PythonScript.ps1 -ScriptPath "fabric/infra/scripts/fabric/remove_fabric_solution.py" -SkipPythonVirtualEnvironment
      interactive: true
      continueOnError: false
```

</details>

<details>
<summary><strong>🚀 GitHub Actions</strong></summary>

These parameters are automatically optimized in [`azure-dev.yml`](../../.github/workflows/azure-dev.yml):

```yaml
- name: Run Fabric Provisioning Script
  run: |
    pwsh ./fabric/infra/scripts/utils/Run-PythonScript.ps1 `
      -ScriptPath "fabric/infra/scripts/fabric/install_fabric_solution.py" `
      -SkipPythonVirtualEnvironment `
      -SkipPythonDependencies `
      -SkipPipUpgrade
```

</details>

</details>

---

## 7. Known Limitations

This section documents known limitations in the deployment process and their workarounds.

###  Graph API Principal (user or service principal) Lookup Limitations

**Issue**: The deployment identity may lack permissions to query user object IDs from Azure Active Directory via Microsoft Graph API.

**Impact**:

- When using `--fabricAdmins` with user principal names (UPNs), the script may fail to resolve user identities
- Service Principals may successfully create workspaces but fail to add human users as administrators
- This can result in workspaces that are only accessible to the deployment service principal

**Technical Details**:
The [`step_workspace_admins.py`](../../infra/scripts/fabric/step_workspace_admins.py) helper module implements fallback logic:

```python
def detect_principal_type(admin_identifier, graph_client=None):
    try:
        # Use Graph API to resolve the principal if available
        if graph_client:
            principal_type, object_id, principal_data = graph_client.resolve_principal(admin_identifier)
            return principal_type, object_id, principal_data
    except GraphApiError as e:
        logger.warning(f"Graph API lookup failed for '{admin_identifier}': {str(e)}")
        logger.warning(f"     Will try both ServicePrincipal and User types...")
        return "Unknown", admin_identifier, {"id": admin_identifier, "displayName": "Unknown"}
```

**Workarounds**:

1. **Use Object IDs Directly**: Configure administrators using their Azure AD object IDs, which don't require Graph API resolution. Get object IDs using Azure CLI:

   ```bash
   # Get user object ID
   az ad user show --id user@contoso.com --query id -o tsv
   
   # Set administrators using object IDs (comma-separated)
   azd env set FABRIC_WORKSPACE_ADMINISTRATORS "87654321-4321-4321-4321-210987654321, 12345678-1234-1234-1234-123456789012"
   azd up
   ```

   The helper module automatically detects whether an identifier is a UPN or object ID and handles accordingly.

2. **Post-Deployment Admin Assignment**: If Graph API permissions cannot be granted, add administrators manually after deployment through the Fabric portal workspace settings, or use the dedicated helper module [`step_workspace_admins.py`](../../infra/scripts/fabric/step_workspace_admins.py) with appropriate credentials that have Graph API access.

---

### 🔐 Fabric REST API Permission Issues

**Issue**: Service Principals may lack sufficient permissions to access Microsoft Fabric REST APIs.

**Impact**:

- Deployment fails during workspace creation or management operations
- Graceful exit with clear guidance on permission requirements

**Technical Details**:
The [`install_fabric_solution.py`](../../infra/scripts/fabric/install_fabric_solution.py) script provides specific error handling for authorization failures:

```python
except FabricApiError as e:
    if e.status_code == 401:
        logger.warning(f"Unauthorized access to Fabric APIs")
        logger.warning("   Please review your Fabric permissions and licensing:")
        logger.warning("   Check these resources:")
        logger.warning("   \u2022 Fabric licenses: https://learn.microsoft.com/fabric/enterprise/licenses")
        logger.warning("   \u2022 Identity support: https://learn.microsoft.com/rest/api/fabric/articles/identity-support")
        logger.warning("   \u2022 Create Entra app: https://learn.microsoft.com/rest/api/fabric/articles/get-started/create-entra-app")
        sys.exit(0)  # Graceful exit with guidance
```

**Resolution**:

1. **Verify Fabric Licensing**: Ensure your organization has appropriate [Microsoft Fabric licenses](https://learn.microsoft.com/fabric/enterprise/licenses)
2. **Review Identity Configuration**: Follow the [Fabric Identity Support](https://learn.microsoft.com/rest/api/fabric/articles/identity-support) documentation
3. **Configure Service Principal**: If using a service principal, ensure it's properly configured following [Create Entra App](https://learn.microsoft.com/rest/api/fabric/articles/get-started/create-entra-app) guidance
4. **Check API Permissions**: Verify the deployment identity has the required Fabric REST API permissions as listed in the [prerequisites](#1-prerequisites)

The script performs a graceful exit (`sys.exit(0)`) rather than failing abruptly, allowing you to resolve permissions and retry the deployment. Both `install_fabric_solution.py` and `remove_fabric_solution.py` use structured logging via Python's `logging` module with level control via the `LOG_LEVEL` environment variable.

---

## 8. Environment Cleanup

When you no longer need your deployed environment, Azure Developer CLI provides a streamlined approach to completely remove all resources and clean up your Microsoft Fabric workspace.

### Complete Environment Removal

The `azd down` command orchestrates a complete environment cleanup process that:

1. **Removes Fabric Workspace**: Safely deletes the Microsoft Fabric workspace and all associated items
2. **Deprovisions Azure Resources**: Removes all Azure infrastructure components deployed via Bicep templates
3. **Preserves Local Environment**: Keeps your local development environment and configurations intact

**Quick cleanup command:**

```bash
# Navigate to your solution directory
cd microsoft-iq-solution-accelerator

# Remove everything deployed by azd up
azd down
```

### Cleanup Process Details

Based on the [`azure.yaml`](../../azure.yaml) configuration, the cleanup process follows these orchestrated steps:

#### Phase 1: Fabric Workspace Cleanup (predown hook)

Before removing Azure infrastructure, the cleanup process first handles the Microsoft Fabric workspace:

**Windows (PowerShell):**

```powershell
./fabric/infra/scripts/utils/Run-PythonScript.ps1 -ScriptPath "fabric/infra/scripts/fabric/remove_fabric_solution.py"
```

**Unix/Linux (PowerShell Core):**

```bash
./fabric/infra/scripts/utils/Run-PythonScript.ps1 -ScriptPath "fabric/infra/scripts/fabric/remove_fabric_solution.py" -SkipPythonVirtualEnvironment
```

This orchestration script ([`Run-PythonScript.ps1`](../../infra/scripts/utils/Run-PythonScript.ps1)) manages:

- **Python Environment Setup**: Creates or reuses Python virtual environment with required dependencies
- **Script Execution**: Runs the specified Python script with proper error handling
- **Cross-Platform Support**: Handles differences between Windows and Unix-based systems

The core removal logic is handled by [`remove_fabric_solution.py`](../../infra/scripts/fabric/remove_fabric_solution.py), which:

- **Workspace Lookup**: Finds the workspace by name (defaults to `Microsoft IQ - {suffix}`) or by ID via `FABRIC_WORKSPACE_ID`
- **Workspace Deletion**: Deletes the entire workspace and all its contents in unattended mode (no interactive confirmation)
- **Error Handling**: Gracefully handles missing workspaces, permission issues, and authorization failures with clear guidance messages
- **Graceful Exit**: Exits with code 0 on non-critical errors to allow infrastructure cleanup to proceed

#### Phase 2: Azure Infrastructure Cleanup

After successful Fabric workspace removal, `azd down` proceeds to deprovision all Azure resources that were created through the [`main.bicep`](../../infra/main.bicep) template, including:

- **Microsoft Fabric Capacity**: Dedicated compute resources
- **Resource Group**: Complete resource group removal (if specified)

### Safety Features

The cleanup process includes several safety mechanisms:

- **Unattended Operation**: The removal script runs without interactive prompts, making it safe for CI/CD pipelines
- **Graceful Error Handling**: Continues with infrastructure cleanup even if Fabric workspace removal fails
- **Detailed Logging**: Provides comprehensive logging output (configurable via `LOG_LEVEL` environment variable) for troubleshooting and audit purposes
- **Non-Destructive Failures**: Missing workspaces or permission issues don't prevent infrastructure cleanup

---

## 9. Additional Resources

- **Documentation**: [Microsoft Fabric](https://learn.microsoft.com/fabric/) | [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- **Repository**: [Solution Accelerator](https://github.com/microsoft/microsoft-iq-solution-accelerator)

For support, visit the [project repository](https://github.com/microsoft/microsoft-iq-solution-accelerator) or engage with the Microsoft Fabric community.

