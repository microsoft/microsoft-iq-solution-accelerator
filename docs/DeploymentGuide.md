# Deployment Guide

Deploy the **Microsoft IQ Solution Accelerator** using Azure Developer CLI to provision a complete enterprise intelligence platform. This automated deployment creates Fabric IQ (data lakehouse, semantic models, ontologies, data agents), Microsoft Foundry (intelligent agents with knowledge base search), and prepares Work IQ (Copilot Studio integration) for manual configuration—all ready to use in minutes.

> 🆘 **Need Help?** If you encounter issues during deployment, check our [Known Issues and Troubleshooting](#known-issues-and-troubleshooting) section for solutions to common problems.

## Key Sections

| Section | Description |
|---------|-------------|
| [**Overview**](#overview) | Two-phase deployment architecture explained |
| [**Prerequisites & Setup**](#step-1-prerequisites--setup) | Azure, Fabric requirements, software installation |
| [**Deployment Environment**](#step-2-choose-your-deployment-environment) | Choose deployment method: Local, Codespaces, Dev Container, or GitHub Actions |
| [**Configuration Settings**](#step-3-configure-deployment-settings-optional) | Optional: Customize resource names and settings |
| [**Deploy the Solution**](#step-4-deploy-the-solution) | Execute deployment with step-by-step instructions |
| [**Post-Deployment Configuration**](#step-5-post-deployment-configuration) | Set up Work IQ (Copilot Studio) and verify components |
| [**Deployment Results**](#step-6-deployment-results) | Verify Azure and Fabric resources |
| [**Clean Up**](#step-7-clean-up-optional) | Remove all deployed resources |
| [**Known Issues and Troubleshooting**](#known-issues-and-troubleshooting) | Common problems and solutions |
| [**Next Steps**](#next-steps) | Additional resources and guides |
| [**Need Help?**](#need-help) | Support options |

---

## Overview

This guide walks you through deploying the Microsoft IQ Solution Accelerator to both Azure and Microsoft Fabric. The deployment process takes approximately 10-15 minutes and provisions a complete enterprise intelligence platform with cloud infrastructure, data foundation, and AI components.

### Two-Phase Architecture

The deployment uses a coordinated two-phase approach that is **idempotent** and **safe to re-run**, automatically detecting existing resources and only creating what's missing:

```text
PHASE 1: Infrastructure (Bicep)           PHASE 2: Solution Bootstrap (Python)
├─ Fabric Capacity                        ├─ Knowledge Base Setup
├─ Microsoft Foundry Hub & Project        ├─ Chat Agent Configuration
├─ Azure OpenAI Model Deployments         ├─ Fabric Workspace
├─ Azure AI Search                        ├─ Workspace Administrators
├─ Azure Storage Account                  ├─ Installer Notebook Upload
└─ Managed Identity                       └─ Run Installer (Lakehouse, Notebooks,
                                              Semantic Models, Ontology, Data Agents)
```

**Phase 1** provisions Azure infrastructure using Bicep templates with ARM idempotency:

- **[Resource Group](https://learn.microsoft.com/azure/azure-resource-manager/management/manage-resource-groups-portal)**: Logical container organizing all deployed Azure resources
- **[Fabric Capacity](https://learn.microsoft.com/fabric/enterprise/licenses#capacity)**: Dedicated compute resources for Fabric workloads (F2-F2048 SKU)
- **[Microsoft Foundry Hub & Project](https://learn.microsoft.com/azure/ai-studio/concepts/ai-resources)**: Core AI platform for agent management
- **[Azure OpenAI Models](https://learn.microsoft.com/azure/ai-services/openai/)**: Chat completion (`gpt-5-mini`) and embedding (`text-embedding-3-small`) deployments
- **[Azure AI Search](https://learn.microsoft.com/azure/search/search-what-is-azure-search)**: Document indexing with vector search for knowledge base
- **[Azure Storage Account](https://learn.microsoft.com/azure/storage/common/storage-account-overview)**: Blob storage for documents with direct citations

**Phase 2** manages solution components using Python scripts with intelligent resource detection:

- **[Knowledge Base](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-create-knowledge-base)**: Azure AI Search index with chunked PDFs and embeddings for hybrid retrieval
- **[Chat Agent](https://learn.microsoft.com/azure/ai-studio/how-to/develop/create-agent)**: AI Foundry agent wired to Knowledge Base via [MCP](https://modelcontextprotocol.io/introduction)
- **[Fabric Workspace](https://learn.microsoft.com/fabric/get-started/workspaces)**: Collaborative environment hosting all Fabric artifacts
  - **[Lakehouse](https://learn.microsoft.com/fabric/data-engineering/lakehouse-overview)**: Unified data platform with sample data
  - **[Notebooks](https://learn.microsoft.com/fabric/data-engineering/how-to-use-notebook)**: Data processing and ingestion pipelines
  - **[Semantic Models](https://learn.microsoft.com/fabric/data-warehouse/semantic-models)**: Business intelligence layer
  - **[Ontology](https://learn.microsoft.com/fabric/data-science/ontology)**: Knowledge graph definitions
  - **[Data Agents](https://learn.microsoft.com/fabric/data-science/ai-services/data-agent-overview)**: AI-powered conversational interface

The entire process is orchestrated by Azure Developer CLI with comprehensive error handling and rollback capabilities.

---

## Step 1: Prerequisites & Setup

### 1.1 Azure Account Requirements

Ensure you have access to an [Azure subscription](https://azure.microsoft.com/free/) with the following permissions:

| Permission | Level | Purpose |
|-----------|-------|---------|
| **Contributor** | Subscription/Resource Group | Deploy Bicep templates and create Azure resources |
| **User Access Administrator** | Subscription/Resource Group | Configure role-based access control (RBAC) |

<details>
<summary><b>How to Check Your Permissions</b></summary>

1. Go to [Azure Portal](https://portal.azure.com/)
2. Search for "Subscriptions" in the top search bar
3. Click on your target subscription
4. Select **Access control (IAM)** from the left menu
5. Look for your user account—you should see **Contributor** or **Owner** role assigned

</details>

### 1.2 Microsoft Fabric Requirements

Your organization must have the following setup:

| Requirement | Details |
|-------------|---------|
| **Fabric License** | [Microsoft Fabric](https://learn.microsoft.com/fabric/admin/fabric-switch) must be enabled in your organization |
| **Fabric Capacity** | Dedicated capacity available for your deployments (or deployment will create one) |
| **Workspace Creation** | Permissions to create new Fabric workspaces |
| **Fabric Admin Portal** | Required tenant settings enabled (see below) |

#### Enable Required Fabric Admin Portal Settings

> **Important:** You must enable Ontology and related preview features in the Fabric Admin Portal before proceeding.

1. Navigate to the [Fabric Admin Portal](https://app.fabric.microsoft.com/admin-portal).

   > If you don't see the **Admin Portal** option, ensure you have **Fabric Admin** or **Global Admin** permissions.

2. In the left-hand navigation pane, select **Tenant settings**.

3. **Enable Ontology (preview):**
   - Search for **Ontology** in the Tenant settings search bar
   - Toggle the setting to **Enabled**
   - Choose whether to enable for **The entire organization** or **Specific security groups**
   - Click **Apply**

4. **Enable Copilot and Azure OpenAI Service:**
   - Search for **Copilot** in the Tenant settings search bar
   - Toggle the setting to **Enabled**
   - Click **Apply**

> **Propagation delay:** These settings may take up to **15 minutes** to take effect across your tenant.

For detailed instructions, refer to the official documentation: [Fabric IQ Tenant Settings](https://learn.microsoft.com/fabric/iq/ontology/overview-tenant-settings).

### 1.3 Deployment Identity

Deployment identity determines how your deployment interacts with Azure and Microsoft Fabric resources. Choose one identity type:

| Identity Type | Best For | Setup Required |
|---------------|----------|----------------|
| **User Account** | Interactive development and testing | Your Azure AD credentials |
| **Service Principal** | Automated deployments and CI/CD pipelines | [Federated identity credentials](https://learn.microsoft.com/azure/developer/github/connect-from-azure-openid-connect) |
| **Managed Identity** | Azure-native automation | Azure subscription access |

### 1.4 Software Requirements

**Note:** Skip this section if using GitHub Codespaces or VS Code Dev Container—all tools are pre-installed in these environments.

Install the following tools on your local machine:

| Tool | Version | Installation |
|------|---------|--------------|
| **Python** | 3.9 or later | [Download from python.org](https://www.python.org/downloads/) |
| **Azure Developer CLI (azd)** | Latest | [Install azd](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) |
| **PowerShell** | 7+ | [Install PowerShell](https://learn.microsoft.com/powershell/scripting/install/installing-powershell) |
| **Git** | Latest | [Download from git-scm.com](https://git-scm.com/downloads) |

<details>
<summary><b>Verify Installation</b></summary>

```bash
python --version
azd version
pwsh --version
git --version
```

</details>

📖 **Detailed Setup:** For complete Azure account configuration, see [Azure Account Setup Guide](./AzureAccountSetUp.md).

---

## Step 2: Choose Your Deployment Environment

Select one of the following options to deploy the solution:

### Environment Comparison

| Environment | Setup Required | Notes |
|-------------|----------------|-------|
| **[GitHub Codespaces](#option-a-github-codespaces)** | GitHub account | Cloud development environment, zero local install |
| **[VS Code Dev Container](#option-b-vs-code-dev-container)** | Docker Desktop + VS Code | Containerized consistency |
| **[Local Machine](#option-c-local-machine)** | Install [software requirements](#14-software-requirements) | Most flexible, requires local setup |
| **[GitHub Actions](#option-d-github-actions)** | Azure service principal | Federated identity, automated deployment |

<details>
<summary><b>Option A: GitHub Codespaces</b></summary>

**Cloud development environment—zero local install required.**

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/microsoft/microsoft-iq-solution-accelerator)

1. Click the **Open in GitHub Codespaces** badge above (or use **Code → Codespaces → Create codespace** on the repository page)
2. Wait for the environment to initialize (2-3 minutes). The `postCreateCommand` runs [`post-create.sh`](../.devcontainer/post-create.sh) and [`setup_env.sh`](../.devcontainer/setup_env.sh) automatically.
3. All tools are pre-installed; proceed to [Step 4: Deploy](#step-4-deploy-the-solution)

> If `azd auth login` opens a browser window that fails to redirect back to the codespace, use `azd auth login --use-device-code`.

See [`.devcontainer/README.md`](../.devcontainer/README.md) for the full list of pre-installed tools and extensions.

</details>

<details>
<summary><b>Option B: VS Code Dev Container</b></summary>

**Consistent development environment using Docker.**



1. Install [Visual Studio Code](https://code.visualstudio.com/)
2. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
3. Install [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) in VS Code
4. Clone the repository:

   ```bash
   git clone https://github.com/microsoft/microsoft-iq-solution-accelerator.git
   cd microsoft-iq-solution-accelerator
   ```

5. Open the folder in VS Code
6. Click "Reopen in Container" when prompted (or run **Command Palette → Dev Containers: Reopen in Container**)
7. All tools are pre-installed; proceed to [Step 4: Deploy](#step-4-deploy-the-solution)

> Existing `azd` credentials from the host's `~/.azure` (or `%USERPROFILE%\.azure`) are bind-mounted into the container, so a previous `azd auth login` carries over.

See [`.devcontainer/README.md`](../.devcontainer/README.md) for configuration details and troubleshooting.

</details>

<details>
<summary><b>Option C: Local Machine</b></summary>

**Full control with your local development environment.**

1. Install the [software requirements](#14-software-requirements) above
2. Clone the repository:

   ```bash
   git clone https://github.com/microsoft/microsoft-iq-solution-accelerator.git
   cd microsoft-iq-solution-accelerator
   ```

3. Proceed to [Step 4: Deploy](#step-4-deploy-the-solution)

</details>

<details>
<summary><b>Option D: GitHub Actions</b></summary>

**Automated CI/CD deployment using GitHub Actions.**

The repository ships with [`.github/workflows/azure-dev.yml`](../.github/workflows/azure-dev.yml), which runs `azd up` end-to-end using **OIDC federated credentials**.

1. Fork the repository to your GitHub account
2. Configure [Azure service principal with federated identity credentials](https://learn.microsoft.com/azure/developer/github/connect-from-azure-openid-connect)
3. Set the following repository secrets in GitHub Settings → Secrets and variables → Actions:
   - `AZURE_CLIENT_ID`: Service principal client ID
   - `AZURE_TENANT_ID`: Azure tenant ID
   - `AZURE_SUBSCRIPTION_ID`: Target subscription ID
4. (Optional) Set additional variables:
   - `FABRIC_WORKSPACE_ADMINISTRATORS`: Comma-separated admin identities
   - `AZURE_AI_DEPLOYMENTS_LOCATION`: AI deployment region
5. Go to **Actions** tab in your GitHub repository
6. Select **CI/CD Azure** workflow
7. Click **Run workflow** and select your branch
8. Monitor the deployment progress in the Actions tab

> You do **not** need to run the [Step 4](#step-4-deploy-the-solution) commands manually for this option—the workflow performs them on your behalf.

</details>

---

## Step 3: Configure Deployment Settings (Optional)

> **Skip to [Step 4](#step-4-deploy-the-solution) if you want to use default settings.**

This section covers all optional configuration settings you can customize before deployment. All settings are configured using `azd env set` commands before running `azd up`.

---

<details>
<summary><b>3.1 Fabric Configuration</b></summary>

**Fabric Capacity:**

```bash
# Use a different Fabric SKU (default: F2)
azd env set FABRIC_CAPACITY_SKU_NAME F4

# Use an existing Fabric capacity (skips creation)
azd env set AZURE_EXISTING_FABRIC_CAPACITY_NAME "my-existing-capacity"

# Add additional capacity admins (JSON array)
azd env set FABRIC_ADMIN_MEMBERS '["user@contoso.com"]'
```

**Available Fabric SKUs:** `F2`, `F4`, `F8`, `F16`, `F32`, `F64`, `F128`, `F256`, `F512`, `F1024`, `F2048`

**Workspace Configuration:**

```bash
# Custom workspace name
azd env set FABRIC_WORKSPACE_NAME "My IQ Workspace"

# Add workspace administrators (comma-separated UPNs or object IDs)
azd env set FABRIC_WORKSPACE_ADMINISTRATORS "user@contoso.com,11111111-2222-3333-4444-555555555555"
```

</details>

---

<details>
<summary><b>3.2 Microsoft Foundry / AI Configuration</b></summary>

**AI Deployment Region (Required if not prompted):**

```bash
azd env set AZURE_AI_DEPLOYMENTS_LOCATION eastus
```

**Available AI Deployment Regions:** `australiaeast`, `eastus`, `eastus2`, `francecentral`, `japaneast`, `swedencentral`, `uksouth`, `westus`, `westus3`

**Model Configuration:**

```bash
# GPT model (default: gpt-5-mini)
azd env set AZURE_OPENAI_DEPLOYMENT_MODEL <your-model>
azd env set AZURE_OPENAI_MODEL_VERSION "<your-model-version>"
azd env set AZURE_OPENAI_DEPLOYMENT_MODEL_CAPACITY <capacity>

# Embedding model (default: text-embedding-3-small)
azd env set AZURE_OPENAI_EMBEDDING_MODEL <your-embedding-model>
azd env set AZURE_OPENAI_EMBEDDING_CAPACITY <capacity>

# Deployment type
azd env set AZURE_OPENAI_MODEL_DEPLOYMENT_TYPE <deployment-type>
```

**Available Deployment Types:** `GlobalStandard`, `Standard`

</details>

---

<details>
<summary><b>3.3 Reuse Existing Resources</b></summary>

If you already have Azure resources that you want to reuse:

```bash
# Use an existing Log Analytics workspace
azd env set AZURE_EXISTING_LOG_ANALYTICS_WORKSPACE_ID "/subscriptions/..."

# Use an existing AI Foundry project
azd env set AZURE_EXISTING_AI_PROJECT_RESOURCE_ID "/subscriptions/..."
```

</details>

---

<details>
<summary><b>3.4 All Configuration Variables</b></summary>

| Category | Variable | Description | Default |
|----------|----------|-------------|---------|
| **Common** | `ENABLE_TELEMETRY` | Enable/disable usage telemetry | `true` |
| **Fabric Capacity** | `FABRIC_CAPACITY_SKU_NAME` | Fabric capacity SKU | `F2` |
| | `AZURE_EXISTING_FABRIC_CAPACITY_NAME` | Use existing capacity | _(empty)_ |
| | `FABRIC_ADMIN_MEMBERS` | Additional capacity admins | `[]` |
| **Fabric Workspace** | `FABRIC_WORKSPACE_NAME` | Workspace name | `Microsoft IQ - {suffix}` |
| | `FABRIC_WORKSPACE_ADMINISTRATORS` | Additional workspace admins | _(empty)_ |
| **Microsoft Foundry** | `AZURE_AI_DEPLOYMENTS_LOCATION` | AI deployment region | _(prompted)_ |
| | `AZURE_OPENAI_DEPLOYMENT_MODEL` | GPT model | `gpt-5-mini` |
| | `AZURE_OPENAI_MODEL_VERSION` | GPT model version | `2025-04-14` |
| | `AZURE_OPENAI_DEPLOYMENT_MODEL_CAPACITY` | GPT capacity (K tokens/min) | `150` |
| | `AZURE_OPENAI_MODEL_DEPLOYMENT_TYPE` | Deployment type | `GlobalStandard` |
| | `AZURE_OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| | `AZURE_OPENAI_EMBEDDING_CAPACITY` | Embedding capacity (K tokens/min) | `80` |
| | `AZURE_SEARCH_SERVICE_LOCATION` | AI Search location | Same as `AZURE_LOCATION` |
| | `AZURE_ENV_USE_CASE` | Industry use case | `Retail-sales-analysis` |
| | `DEPLOYING_USER_PRINCIPAL_TYPE` | Principal type for CI/CD | `User` |

**Available Use Cases:** `Retail-sales-analysis`, `Insurance-improve-customer-meetings`

</details>

---

## Step 4: Deploy the Solution

### 4.1 Clone Repository (If Needed)

If you haven't already cloned the repository, do so now:

```bash
git clone https://github.com/microsoft/microsoft-iq-solution-accelerator.git
cd microsoft-iq-solution-accelerator
```

### 4.2 Authenticate with Azure

```bash
# Login to Azure Developer CLI
azd auth login

# For specific Azure tenants:
azd auth login --tenant-id <your-tenant-id>
```

> **Note: Finding Your Tenant ID:**
>
> 1. Open [Azure Portal](https://portal.azure.com/)
> 2. Go to Microsoft Entra ID
> 3. Copy the **Tenant ID** from the Overview section

### 4.3 Configure Settings (Optional)

> See [Step 3: Configure Deployment Settings](#step-3-configure-deployment-settings-optional) for all configuration options including:
> - Fabric capacity and workspace settings
> - AI deployment region and model configuration
> - Reusing existing Azure/Fabric resources

### 4.4 Start Deployment

Run the deployment command:

```bash
azd up
```

During deployment, you'll be prompted for:

1. **Environment name** (e.g., "miqdev"): Used to build the name of deployed Azure resources
2. **Azure subscription**: Select your target subscription
3. **AI Deployments location** (`aiDeploymentsLocation`): Select the region for AI model deployments
4. **Resource group**: Choose to create a new resource group or use an existing one
5. **Resource group location**: Select the region for the resource group
6. **Resource group name**: Enter a name for the new resource group (e.g., "rg-miqdev")

**What Happens During Deployment:**

| Phase | Step | Description |
|-------|------|-------------|
| **Phase 1** | Infrastructure | Provision Fabric Capacity, Foundry Hub/Project, AI Search, Storage, OpenAI models |
| **Phase 2** | `setup_knowledge_base` | Create search index, upload PDFs, provision knowledge base |
| | `setup_agent` | Create AI Foundry chat agent with Knowledge Base MCP tool (**Best-effort**) |
| | `setup_workspace` | Create or find Fabric workspace, assign to capacity |
| | `setup_administrators` | Add workspace administrators |
| | `upload_installer` | Upload installer notebook to workspace |
| | `run_installer` | Execute notebook to deploy lakehouse, notebooks, semantic models, ontology, data agents |

The entire deployment typically completes in **10-15 minutes**.

### 4.5 Verify Deployment Success

After `azd up` completes successfully:

- ✅ Check the deployment summary displayed in your terminal
- ✅ Verify resources in [Azure Portal](https://portal.azure.com/)
- ✅ Confirm your Fabric workspace in [Fabric Portal](https://app.fabric.microsoft.com)

⚠️ **Deployment Issues?** Check [Known Issues and Troubleshooting](#known-issues-and-troubleshooting) for common solutions.

> **Preview Feature Notice:** If the Agent setup fails during deployment (step `setup_agent`), the core functionality will still work. You can verify and retry by running `azd up` again.

---

## Step 5: Post-Deployment Configuration

### 5.1 Work IQ (Copilot Studio) Setup

The `azd up` workflow provisions **Fabric IQ** and **Microsoft Foundry**. The third component—**Work IQ** (Copilot Studio email-triggered agent)—is deployed **manually** after `azd up` completes.

> 👉 **[Copilot Studio Integration — Deployment Guide](./copilot/DeploymentGuide.md)**

**Summary of Manual Steps:**

1. **Import the solution**: Import the Power Platform zip solution from [src/copilot/sln](../src/copilot/sln) into your Power Platform environment
2. **Configure connections**: Sign in to Work IQ, Microsoft Teams, Copilot Studio, Office 365 Outlook, Fabric Data Agent, and Foundry Agent connections
   - The Foundry Agent connection uses the `AZURE_AI_AGENT_ENDPOINT` value from `azd env get-values`
   - The Fabric Data Agent connection requires the workspace name or ID from `azd env get-values` → `FABRIC_WORKSPACE_NAME`
3. **Configure email trigger**: In the Power Automate cloud flow **When a New Email Arrives (V3)**, select the target inbox/folder to monitor
4. **Publish the agent**: In [Copilot Studio](https://copilotstudio.microsoft.com), publish and enable the **Microsoft Teams** channel

For architecture overview, see [docs/copilot/README.md](./copilot/README.md). For end-to-end QA, see [Copilot Studio Testing Guide](./copilot/TestingGuide.md).

### 5.2 Verify Fabric Data Agent

The Fabric Data Agent is automatically configured during deployment to answer natural language questions about your data.

**Access your workspace:**

1. Open [Microsoft Fabric portal](https://app.fabric.microsoft.com)
2. Switch to **Fabric Developer** experience (top-right)
3. Select your workspace (default: `Microsoft IQ - {suffix}`)
4. Navigate to the Data Agent item

### 5.3 Verify Microsoft Foundry Agent

**Access your Foundry project:**

1. Open [ai.azure.com](https://ai.azure.com)
2. Select your hub and project (project name from `azd env get-values` → `AZURE_AI_PROJECT_NAME`)
3. Verify:
   - **Knowledge Bases** → `{solution_suffix}-kb` exists with status *Ready*
   - **Agents** → `ChatAgent` exists with Knowledge Base MCP tool attached
   - **Connections** → AI Search, Blob Storage, and KB MCP connections are *Connected*

**Test the agent from CLI:**

```bash
python infra/scripts/foundry/test_agent.py
```

### 5.4 Explore Sample Features

- **Real-Time Dashboard:** Open the Power BI reports in the Fabric workspace to monitor data
- **Data Agent:** Ask natural language questions about your data through the Fabric Data Agent
- **Chat Agent:** Query documents through the Foundry Chat Agent

---

## Step 6: Deployment Results

### Azure Infrastructure

After successful deployment, you have:

| Resource | Purpose | Details |
|----------|---------|---------|
| **Fabric Capacity** | Compute for Fabric workloads | Auto-scaled, dedicated capacity |
| **Microsoft Foundry Hub & Project** | AI platform for agents | Contains model deployments, connections |
| **Azure OpenAI deployments** | AI models | `gpt-5-mini` (chat), `text-embedding-3-small` (embeddings) |
| **Azure AI Search** | Document indexing | Vector + keyword search for knowledge base |
| **Azure Storage Account** | Document storage | Blob storage for source documents |
| **Log Analytics + App Insights** | Monitoring | Diagnostic and monitoring sink |
| **User-assigned Managed Identity** | Security | Used by deployment scripts and connections |

**Access in Azure Portal:** Open [portal.azure.com](https://portal.azure.com) → **Resource groups** → select your resource group (value of `AZURE_RESOURCE_GROUP` from `azd env get-values`).

### Fabric Workspace

**Workspace Name:** `Microsoft IQ - {suffix}`

**Contents:**

```text
Microsoft IQ - {suffix}
├── 📊 Lakehouses
│   └── miqsadata (with sample data tables)
├── 📓 Notebooks
│   ├── pipeline_main (data ingestion orchestrator)
│   ├── pipeline_update (pipeline maintenance)
│   ├── data_processing/ (per-domain load notebooks)
│   └── schema/ (per-domain table schemas)
├── 📈 Semantic Models & Reports
│   ├── RetailSupplyChainModel.SemanticModel
│   ├── Sales Overview.SemanticModel
│   ├── Sales Overview.Report
│   ├── Supply Chain Management.SemanticModel
│   └── Supply Chain Management.Report
├── 🧬 Ontologies
│   └── RetailSupplyChainOntologyModel
└── 🤖 Data Agents
    └── RetailSC Ontology Agent
```

**Access:** Open [app.fabric.microsoft.com](https://app.fabric.microsoft.com) → Switch to **Fabric Developer** → Select your workspace.

### Microsoft Foundry Components

| Component | Default Name | Purpose |
|-----------|--------------|---------|
| **Search Index** | `{solution_suffix}-documents` | Chunked PDFs with embeddings for hybrid retrieval |
| **Knowledge Source** | `{solution_suffix}-ks` | Pointer to AI Search index |
| **Knowledge Base** | `{solution_suffix}-kb` | Automatic query planning over knowledge source |
| **KB MCP Connection** | `{solution_suffix}-kb-mcp-connection` | Exposes Knowledge Base to agent via MCP |
| **Chat Agent** | `ChatAgent` | AI agent for document Q&A with citations |

### Environment Variables

View all deployment outputs with:

```bash
azd env get-values
```

**Key outputs:**

| Variable | Description |
|----------|-------------|
| `AZURE_AI_AGENT_ENDPOINT` | Microsoft Foundry agent endpoint |
| `AZURE_AI_SEARCH_ENDPOINT` | Search service endpoint |
| `AZURE_STORAGE_BLOB_ENDPOINT` | Document storage endpoint |
| `AZURE_FABRIC_CAPACITY_NAME` | Fabric capacity name |
| `FABRIC_WORKSPACE_ID` | Fabric workspace ID |
| `SOLUTION_NAME` / `SOLUTION_SUFFIX` | Solution identifier |

---

## Step 7: Clean Up (Optional)

### Remove All Resources

When you no longer need the deployment:

```bash
# Navigate to your solution directory
cd microsoft-iq-solution-accelerator

# Remove everything deployed by azd up
azd down --force --purge
```

**What Gets Cleaned Up:**

- ✅ Fabric workspace and all components
- ✅ Azure infrastructure (Foundry, AI Search, Storage, OpenAI deployments)
- ✅ Fabric capacity (if created by deployment)
- ✅ Resource groups and configurations

**What Gets Preserved:**

- ✅ Local development files
- ✅ Environment configurations (unless `--purge` is used)
- ✅ Source code

### Manual Cleanup (If Needed)

If automated cleanup fails:

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to Resource Groups
3. Select your resource group
4. Click **Delete resource group**
5. Confirm deletion

> **Note:** This command removes all Azure resources. Ensure you've backed up any important data before running cleanup.

---

## Known Issues and Troubleshooting

### Fabric REST API Permission Issues

**Problem:** Deployment fails during workspace or component creation

**Symptoms:**

- Error mentions "insufficient permissions" or "unauthorized access"
- Workspace creation fails

**Resolution:**

1. **Verify Fabric Licensing**: Ensure your organization has appropriate [Microsoft Fabric licenses](https://learn.microsoft.com/fabric/enterprise/licenses)

2. **Verify Organization Setup:**
   - Confirm [Microsoft Fabric is enabled](https://learn.microsoft.com/fabric/admin/fabric-switch) in your organization
   - Check that appropriate Fabric licenses are assigned

3. **Enable Required Tenant Settings:**
   - Go to [Fabric Admin Portal](https://app.fabric.microsoft.com/admin-portal)
   - Navigate to Tenant settings
   - Enable **Ontology (preview)** and **Copilot and Azure OpenAI Service**

4. **Verify Azure Permissions:**
   - Confirm deployment identity has **Contributor** or **Owner** role on subscription/resource group
   - Check that **Microsoft.Fabric** resource provider is registered

### Agent Setup Fails (Best-Effort)

**Problem:** The `setup_agent` step completes with a warning

**Resolution:** This is expected behavior—the step uses best-effort semantics. Verify the agent in the [Foundry portal](https://ai.azure.com):

1. Navigate to your project
2. Check **Agents** → `ChatAgent` exists
3. If missing, re-run `azd up`

### Propagation Delays

**Problem:** Ontology or Data Agent options not visible in Fabric workspace

**Resolution:** Tenant settings may take up to **15 minutes** to propagate. Wait and refresh the page.

### Azure Foundry Agent Publish — Protocol Error

**Problem:** Agent deployment fails with HTTP 400 error indicating a protocol mismatch between the client and the agent endpoint

**Error Message:**

```
The connector 'Azure AI Foundry Agent Service' returned an HTTP error with code 400.
Inner Error: Agent endpoint does not support activity. Please update the agent endpoint to support this protocol.
```

**Symptoms:**

- Agent publish fails with protocol error during Copilot Studio integration
- Connection attempt shows "endpoint does not support activity" message
- Agent is unreachable from Teams or Work IQ

**Resolution:**

Fix — enable the Activity Protocol in the Foundry portal
1. Open Microsoft Foundry portal → your project → Agents → ChatAgent.
2. Click Deploy (or Channels / Endpoints, depending on portal version) in the agent's top-right menu.
3. Enable "Connect to Copilot Studio" or "Enable Activity Protocol" or "Publish to channels → Direct Line" — the label varies with the portal build.
4. Copy the new activity-protocol endpoint that appears (it will end in something like /agents/ChatAgent/activity instead of /api/projects/...).
5. In Copilot Studio → your agent → Agents → Microsoft Foundry connection → Edit → paste the new endpoint → Save.
6. Test again.

### Graph Not Loading in Fabric

**Problem:** The ontology graph or knowledge graph view does not load in the Fabric workspace

**Symptoms:**

- Graph view is blank or stuck loading
- No nodes or edges appear after workspace deployment

**Resolution:**

Tenant settings changes (Ontology preview, Data Agents) can take up to **15 minutes** to propagate across the tenant. Wait 15 minutes, then:

1. Refresh the browser tab
2. If using the Fabric desktop app, sign out and sign back in
3. If the graph still does not appear, confirm that **Ontology (preview)** is enabled in your [Fabric Admin Portal](https://app.fabric.microsoft.com/admin-portal) under **Tenant settings**

### Teams Agent Not Responding

**Problem:** The Work IQ agent in Microsoft Teams does not respond to messages

**Symptoms:**

- Agent is visible in Teams but does not reply
- Messages appear sent but no response is received

**Resolution:**

1. **Verify the agent is published**: In [Copilot Studio](https://copilotstudio.microsoft.com), confirm the agent has been published at least once and the **Teams** channel is enabled

2. **Refresh Teams cache**: Teams caches app configurations — sign out and sign back into the Teams desktop client, or refresh the browser if using Teams on the web

3. **Disconnect and reconnect the Teams channel**:
   1. In Copilot Studio, open your agent and select **Channels**
   2. Select the **Teams and Microsoft 365 Copilot** tile
   3. Select **Remove channel** and confirm **Disconnect**
   4. Wait a few minutes, then select **Add channel** to reconnect
   5. Republish the agent and reinstall it in Teams via **See agent in Teams** → **Add**

4. **Use Teams on the web as a fallback**: Navigate to [teams.microsoft.com](https://teams.microsoft.com) to interact with the agent while the desktop client cache refreshes

5. **Check connection authorizations**: In the Power Platform solution, ensure all connections (Work IQ, Microsoft Teams, Copilot Studio, Office 365 Outlook) are signed in and authorized — unauthorized connections silently prevent the agent from responding

### For Additional Help

- Review [Technical Architecture](./TechnicalArchitecture.md) for system design questions
- See [FAQ](./FAQs.md) for common questions

---

## Next Steps

Now that deployment is complete, explore these resources:

- **[Copilot Studio Deployment](./copilot/DeploymentGuide.md)**: Complete Work IQ setup
- **[Copilot Studio Testing](./copilot/TestingGuide.md)**: End-to-end QA testing
- **[Manual Fabric Deployment](./fabric/DeploymentGuideFabricManual.md)**: Fabric workspace only (no Azure infrastructure)
- **[Foundry Deep-Dive](./foundry/DeploymentGuideFoundry.md)**: Foundry-specific details
- **[Technical Architecture](./TechnicalArchitecture.md)**: System design and data flow

---

## Need Help?

- 🐛 **Issues:** Check [Known Issues and Troubleshooting](#known-issues-and-troubleshooting) section above
- 🐞 **Report Issue:** [Open a GitHub Issue](https://github.com/microsoft/microsoft-iq-solution-accelerator/issues/new) for bugs or problems
- 💬 **Support:** Review [Support Guidelines](../SUPPORT.md)
- 🔧 **Contributing:** See [Contributing Guide](../CONTRIBUTING.md)
- 📖 **FAQs:** Check [Frequently Asked Questions](./FAQs.md)

---

## Additional Resources

- **Azure Developer CLI Documentation:** [learn.microsoft.com/azure/developer/azure-developer-cli](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview)
- **Microsoft Fabric Documentation:** [learn.microsoft.com/fabric](https://learn.microsoft.com/fabric/)
- **Microsoft Foundry Documentation:** [learn.microsoft.com/azure/foundry](https://learn.microsoft.com/azure/foundry/what-is-foundry)
- **GitHub Repository:** [microsoft/microsoft-iq-solution-accelerator](https://github.com/microsoft/microsoft-iq-solution-accelerator)
