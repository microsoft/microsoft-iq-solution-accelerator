# Deployment Guide - Microsoft IQ Solution Accelerator

Deploy the complete **Microsoft IQ Solution Accelerator** using Azure Developer CLI in minutes. This deployment provisions Fabric IQ (data platform) and Microsoft Foundry (intelligent agents) components.

---

## Introduction

The Microsoft IQ Solution Accelerator is an end-to-end data and AI platform that combines:

- **Fabric IQ**: Data lakehouse, notebooks, semantic models, and data agents for unified data foundation
- **Microsoft Foundry**: Intelligent agents with knowledge base search for document-based question answering

The deployment is fully automated and idempotent, using Azure Developer CLI to orchestrate infrastructure provisioning and post-deployment configuration.

---

## Deployment Overview

### Infrastructure Provisioned

The deployment creates two integrated components in a single Azure Resource Group:

#### 1. Fabric IQ Resources
- **[Fabric Capacity](https://learn.microsoft.com/fabric/enterprise/licenses)**: Compute engine (F2-F2048 SKU) powering data workloads
- **[Fabric Workspace](https://learn.microsoft.com/fabric/get-started/workspaces)**: Organized workspace containing:
  - [Lakehouse](https://learn.microsoft.com/fabric/data-engineering/lakehouse-overview) with ingested sample data
  - [Data processing notebooks](https://learn.microsoft.com/fabric/data-engineering/how-to-use-notebook)
  - [Semantic models](https://learn.microsoft.com/fabric/data-warehouse/semantic-models) and [reports](https://learn.microsoft.com/power-bi/create-reports/service-report-create-new)
  - [Ontology definitions](https://learn.microsoft.com/fabric/data-science/ontology)
  - [Data agents](https://learn.microsoft.com/fabric/data-science/ai-services/data-agent-overview)

#### 2. Microsoft Foundry Resources
- **[Microsoft Foundry Hub & Project](https://learn.microsoft.com/azure/ai-studio/concepts/ai-resources)**: Core AI platform for agent management
- **[Azure AI Search](https://learn.microsoft.com/azure/search/search-what-is-azure-search)**: Document indexing with [vector search](https://learn.microsoft.com/azure/search/vector-search-overview) and [Knowledge Base](https://learn.microsoft.com/azure/ai-foundry/concepts/knowledge-bases)
- **[Azure Storage Account](https://learn.microsoft.com/azure/storage/common/storage-account-overview)**: [Blob storage](https://learn.microsoft.com/azure/storage/blobs/storage-blobs-overview) for documents with direct citations
- **[Azure OpenAI Models](https://learn.microsoft.com/azure/ai-services/openai/)**:
  - [`gpt-4.1-mini`](https://learn.microsoft.com/azure/ai-services/openai/concepts/models) - Chat completion (150K TPM)
  - [`text-embedding-3-small`](https://learn.microsoft.com/azure/ai-services/openai/concepts/models#embeddings) - Vector embeddings (80K TPM)
- **[Chat Agent](https://learn.microsoft.com/azure/ai-studio/how-to/develop/create-agent)**: Knowledge Base-powered agent for document Q&A

### Deployment Phases

The deployment follows a **two-phase automated workflow**:

#### Phase 1: Infrastructure (Bicep)
Provisions all Azure resources via [`main.bicep`](../infra/main.bicep):
- Fabric capacity and [managed identity](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview)
- [Microsoft Foundry hub](https://learn.microsoft.com/azure/ai-studio/concepts/ai-resources), [project](https://learn.microsoft.com/azure/ai-studio/how-to/create-projects), and [connections](https://learn.microsoft.com/azure/ai-studio/how-to/connections-add)
- AI Search service and Storage account
- [OpenAI model deployments](https://learn.microsoft.com/azure/ai-services/openai/how-to/create-resource)

#### Phase 2: Solution Bootstrap (Python)
Orchestrated by [`install_microsoft_iq_solution.py`](../infra/scripts/install_microsoft_iq_solution.py), which runs as the `azd up` post-provision hook and executes 6 steps in order:

1. **`setup_knowledge_base`** — Create the Azure AI Search index, upload PDFs from [`src/foundry/data/documents/`](../src/foundry/data/documents/), and provision the Foundry IQ knowledge source and knowledge base (via [`foundry/step_knowledge_base.py`](../infra/scripts/foundry/step_knowledge_base.py)).
2. **`setup_agent`** — Create the AI Foundry chat agent wired up to the Knowledge Base via [MCP](https://modelcontextprotocol.io/introduction) (via [`foundry/step_agent_setup.py`](../infra/scripts/foundry/step_agent_setup.py)). Runs in best-effort mode: transient platform errors are recorded as warnings and the deployment continues.
3. **`setup_workspace`** — Create or find the Fabric workspace and assign it to the capacity, resuming the capacity if paused (via [`fabric/step_workspace_setup.py`](../infra/scripts/fabric/step_workspace_setup.py)).
4. **`setup_administrators`** — Add [workspace administrators](https://learn.microsoft.com/fabric/get-started/roles-workspaces) using [Graph API](https://learn.microsoft.com/graph/overview) resolution with fallback (via [`fabric/step_workspace_admins.py`](../infra/scripts/fabric/step_workspace_admins.py)).
5. **`upload_installer`** — Upload [`fabric_solution_installer.ipynb`](../infra/fabric/deploy/fabric_solution_installer.ipynb), patched in-memory with the current git branch and `GITHUB_TOKEN` if set (via [`fabric/step_notebook_installer.py`](../infra/scripts/fabric/step_notebook_installer.py)).
6. **`run_installer`** — Execute the installer notebook as a Fabric job. The notebook uses [`fabric-launcher`](https://github.com/microsoft/fabric-launcher) to deploy items from [`src/fabric/fabric_workspace/`](../src/fabric/fabric_workspace/), then runs post-deployment tasks: `pipeline_main` for data ingestion, ontology deployment, and folder organization.

Both phases execute automatically with a single `azd up` command.

---

## Deployment Commands

### Prerequisites

Ensure you have the following installed:
- **[Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)** (azd)
- **[Python 3.9+](https://www.python.org/downloads/)**

You also need:
- **Azure subscription** with permissions to create resources
- **Microsoft Fabric** enabled on your subscription ([register provider](https://learn.microsoft.com/azure/azure-resource-manager/management/resource-providers-and-types))

### Deploy Locally

Run the following commands in a single bash session:

```bash
# Clone the repository
git clone https://github.com/microsoft/microsoft-iq-solution-accelerator.git
cd microsoft-iq-solution-accelerator

# (Optional) Set GitHub token for private repositories
# The Fabric deployment pulls workspace items from GitHub
# Create a token with 'repo' scope and read permisssions for 'Contents' at https://github.com/settings/personal-access-tokens
azd env set GITHUB_TOKEN "your-github-token" # optional

# Authenticate with Azure
azd auth login

# Deploy the solution
# This will prompt you to select Azure subscription and region,
# then provision all infrastructure and run post-deployment scripts
azd up

# (Optional) View all deployment outputs
azd env get-values
```

The entire deployment typically completes in **10-15 minutes**.

### Re-running Deployment

The deployment is **idempotent** and safe to re-run:
```bash
azd up
```

- Existing resources are updated (not recreated)
- Fabric workspace content is refreshed to latest version
- New administrators can be added without affecting existing ones

---

## Optional Configuration Variables

Customize your deployment by setting `azd` environment variables before running `azd up`. Use `azd env set <VARIABLE> <value>` to configure any of the following:

| Category | Variable | Description | Default | Example |
|----------|----------|-------------|---------|---------|
| **Common** | `ENABLE_TELEMETRY` | Enable/disable usage telemetry | `true` | `azd env set ENABLE_TELEMETRY false` |
| **Fabric Capacity** | `FABRIC_CAPACITY_SKU_NAME` | Fabric capacity SKU | `F2` | `azd env set FABRIC_CAPACITY_SKU_NAME F4` |
| | `AZURE_EXISTING_FABRIC_CAPACITY_NAME` | Use an existing Fabric capacity (skips creation) | _(empty)_ | `azd env set AZURE_EXISTING_FABRIC_CAPACITY_NAME "my-capacity"` |
| | `FABRIC_ADMIN_MEMBERS` | Additional Fabric capacity admins (JSON array of UPNs or object IDs) | `[]` | `azd env set FABRIC_ADMIN_MEMBERS '["user@contoso.com"]'` |
| **Fabric Workspace** | `FABRIC_WORKSPACE_NAME` | Override the default Fabric workspace name | `Microsoft IQ - {suffix}` | `azd env set FABRIC_WORKSPACE_NAME "My Workspace"` |
| | `FABRIC_WORKSPACE_ADMINISTRATORS` | Comma-separated additional workspace admins | _(empty)_ | `azd env set FABRIC_WORKSPACE_ADMINISTRATORS "user@contoso.com"` |
| **Microsoft Foundry** | `AZURE_AI_DEPLOYMENTS_LOCATION` | AI deployment region (**required**) | _(prompted)_ | `azd env set AZURE_AI_DEPLOYMENTS_LOCATION eastus` |
| | `AZURE_OPENAI_DEPLOYMENT_MODEL` | GPT model to deploy | `gpt-4.1-mini` | `azd env set AZURE_OPENAI_DEPLOYMENT_MODEL gpt-4o` |
| | `AZURE_OPENAI_MODEL_VERSION` | GPT model version | `2025-04-14` | `azd env set AZURE_OPENAI_MODEL_VERSION 2025-04-14` |
| | `AZURE_OPENAI_DEPLOYMENT_MODEL_CAPACITY` | GPT capacity (tokens/min in thousands) | `150` | `azd env set AZURE_OPENAI_DEPLOYMENT_MODEL_CAPACITY 200` |
| | `AZURE_OPENAI_MODEL_DEPLOYMENT_TYPE` | GPT deployment type | `GlobalStandard` | `azd env set AZURE_OPENAI_MODEL_DEPLOYMENT_TYPE Standard` |
| | `AZURE_OPENAI_EMBEDDING_MODEL` | Embedding model to deploy | `text-embedding-3-small` | `azd env set AZURE_OPENAI_EMBEDDING_MODEL text-embedding-3-small` |
| | `AZURE_OPENAI_EMBEDDING_CAPACITY` | Embedding capacity (tokens/min in thousands) | `80` | `azd env set AZURE_OPENAI_EMBEDDING_CAPACITY 120` |
| | `AZURE_SEARCH_SERVICE_LOCATION` | Azure AI Search service location | Same as `AZURE_LOCATION` | `azd env set AZURE_SEARCH_SERVICE_LOCATION eastus` |
| | `AZURE_ENV_USE_CASE` | Industry use case scenario | `Retail-sales-analysis` | `azd env set AZURE_ENV_USE_CASE Insurance-improve-customer-meetings` |
| | `AZURE_EXISTING_LOG_ANALYTICS_WORKSPACE_ID` | Use an existing Log Analytics workspace | _(empty)_ | `azd env set AZURE_EXISTING_LOG_ANALYTICS_WORKSPACE_ID "/subscriptions/..."` |
| | `AZURE_EXISTING_AI_PROJECT_RESOURCE_ID` | Use an existing AI Foundry project | _(empty)_ | `azd env set AZURE_EXISTING_AI_PROJECT_RESOURCE_ID "/subscriptions/..."` |
| | `DEPLOYING_USER_PRINCIPAL_TYPE` | Deploying principal type (use `ServicePrincipal` for CI/CD with OIDC) | `User` | `azd env set DEPLOYING_USER_PRINCIPAL_TYPE ServicePrincipal` |
| **GitHub** | `GITHUB_TOKEN` | GitHub Personal Access Token (for private repos) | _(empty)_ | `azd env set GITHUB_TOKEN "ghp_..."` |

**Available Fabric SKUs**: `F2`, `F4`, `F8`, `F16`, `F32`, `F64`, `F128`, `F256`, `F512`, `F1024`, `F2048`

**Available AI Deployment Regions**: `australiaeast`, `eastus`, `eastus2`, `francecentral`, `japaneast`, `swedencentral`, `uksouth`, `westus`, `westus3`

**Available Use Cases**: `Retail-sales-analysis`, `Insurance-improve-customer-meetings`

**Available Deployment Types**: `GlobalStandard`, `Standard`

---

## Deployment Results

After successful deployment, you will have:

### Fabric IQ Components

**Workspace Structure** (deployed from [`src/fabric/fabric_workspace/`](../src/fabric/fabric_workspace/)):
```
Microsoft IQ - {suffix}
├── 📊 Lakehouses
│   └── miqsadata (with sample data tables)
├── 📓 Notebooks
│   ├── pipeline_main          (data ingestion orchestrator)
│   ├── pipeline_update        (pipeline maintenance)
│   ├── data_processing/       (per-domain load notebooks)
│   ├── schema/                (per-domain table schemas)
│   └── …
├── 📈 Semantic Models & Reports
│   ├── RetailSupplyChainModel.SemanticModel
│   └── Supply Chain Management.SemanticModel
├── 🧬 Ontologies
│   └── RetailSupplyChainOntologyModel
└── 🤖 Data Agents
    └── RetailSC Ontology Agent
```

Access your workspace:
- Open [Microsoft Fabric portal](https://app.fabric.microsoft.com)
- Navigate to your workspace (default name: `Microsoft IQ - {SOLUTION_SUFFIX}`)

### Microsoft Foundry Components

**Deployed Services**:
- **Microsoft Foundry Project**: Accessible at the endpoint shown in deployment output
- **Search Index**: `{solutionName}-documents` with vector search enabled
- **Knowledge Base**: `{solutionName}-kb` with automatic query planning
- **Chat Agent**: Ready to answer questions about uploaded documents

**Test the Agent**:
```bash
# From the repository root
python infra/scripts/foundry/test_agent.py
```

### Environment Variables

All connection details are saved in your azd environment. View them with:
```bash
azd env get-values
```

Key outputs:
- `AZURE_AI_AGENT_ENDPOINT` - Microsoft Foundry agent endpoint
- `AZURE_AI_SEARCH_ENDPOINT` - Search service endpoint
- `AZURE_STORAGE_BLOB_ENDPOINT` - Document storage endpoint
- `AZURE_FABRIC_CAPACITY_NAME` - Fabric capacity name
- `SOLUTION_NAME` - Your solution identifier

### Next Steps

1. **Add Your Documents**: Upload PDFs to [`src/foundry/data/documents/`](../src/foundry/data/documents/) and re-run the deployment to refresh the knowledge base:
   ```bash
   azd up
   ```
   This re-executes `setup_knowledge_base` (Step 1), which re-uploads PDFs to blob storage and re-indexes them.

2. **Explore Fabric Workspace**: Open notebooks and run data pipelines

3. **Test the Agent**: Use the test script to query your documents

4. **View Dashboards**: Access reports in Fabric workspace

---

## Environment Cleanup

To remove all deployed resources:

```bash
azd down
```

This command:
- Runs the `predown` hook ([`remove_microsoft_iq_solution.py`](../infra/scripts/remove_microsoft_iq_solution.py)) to delete the Fabric workspace
- Deletes the Azure Resource Group and all resources inside it (including the Fabric capacity)
- Preserves your local `.azure/{environment}` configuration unless you also pass `--purge`

---

## Additional Resources

- **Detailed Fabric Deployment Guide**: [DeploymentGuideFabric.md](./fabric/DeploymentGuideFabric.md)
- **Azure Developer CLI Documentation**: [learn.microsoft.com/azure/developer/azure-developer-cli](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview)
- **Microsoft Fabric Documentation**: [learn.microsoft.com/fabric](https://learn.microsoft.com/fabric/)
- **Microsoft Foundry Documentation**: [learn.microsoft.com/azure/foundry](https://learn.microsoft.com/azure/foundry/what-is-foundry)
- **GitHub Repository**: [microsoft/microsoft-iq-solution-accelerator](https://github.com/microsoft/microsoft-iq-solution-accelerator)