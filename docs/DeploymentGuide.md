# Deployment Guide - Microsoft IQ Solution Accelerator

Deploy the complete **Microsoft IQ Solution Accelerator** using Azure Developer CLI in minutes. This deployment provisions Fabric IQ (data platform) and Microsoft Foundry (intelligent agents) components.

---

## Introduction

The Microsoft IQ Solution Accelerator is an end-to-end data and AI platform that combines:

- **Fabric IQ**: Data lakehouse, notebooks, semantic models, and data agents for unified data foundation
- **Microsoft Foundry**: Intelligent agents with knowledge base search for document-based question answering

The deployment is fully automated and idempotent, using Azure Developer CLI to orchestrate infrastructure provisioning and post-deployment configuration.

### Table of Contents

1. [Deployment Overview](#deployment-overview)
   - [Infrastructure Provisioned](#infrastructure-provisioned)
   - [Deployment Phases](#deployment-phases)
2. [Deployment Environment Setup](#deployment-environment-setup)
3. [Deployment Commands](#deployment-commands)
4. [Optional Configuration Variables](#optional-configuration-variables)
5. [Deployment Results](#deployment-results)
   - [Azure Resources (Resource Group)](#azure-resources-resource-group)
   - [Fabric IQ Components](#fabric-iq-components)
   - [Microsoft Foundry Components](#microsoft-foundry-components)
   - [Environment Variables](#environment-variables)
   - [Next Steps](#next-steps)
6. [Environment Cleanup](#environment-cleanup)
7. [Additional Resources](#additional-resources)

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

The deployment follows a **two-phase automated workflow**, both phases triggered by a single `azd up` command:

| # | Phase | Driver | Step / Resource | Description |
|---|---|---|---|---|
| — | **Phase 1: Infrastructure** | [`main.bicep`](../infra/main.bicep) (Bicep) | Fabric capacity & [managed identity](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview) | Provision the [Fabric capacity](https://learn.microsoft.com/fabric/enterprise/licenses) and the user-assigned managed identity used by deployment scripts. |
| — | | | [Microsoft Foundry hub](https://learn.microsoft.com/azure/ai-studio/concepts/ai-resources), [project](https://learn.microsoft.com/azure/ai-studio/how-to/create-projects) & [connections](https://learn.microsoft.com/azure/ai-studio/how-to/connections-add) | Create the Foundry hub/project and the AI Search + Storage connections. |
| — | | | AI Search service & Storage account | Provision the indexer + blob storage backing the knowledge base. |
| — | | | [OpenAI model deployments](https://learn.microsoft.com/azure/ai-services/openai/how-to/create-resource) | Deploy the chat completion and embedding models. |
| 1 | **Phase 2: Solution Bootstrap** | [`install_microsoft_iq_solution.py`](../infra/scripts/install_microsoft_iq_solution.py) (Python, `postprovision` hook) | `setup_knowledge_base` ([`step_knowledge_base.py`](../infra/scripts/foundry/step_knowledge_base.py)) | Create the Azure AI Search index, upload PDFs from [`src/foundry/data/documents/`](../src/foundry/data/documents/), and provision the Foundry IQ knowledge source and knowledge base. |
| 2 | | | `setup_agent` ([`step_agent_setup.py`](../infra/scripts/foundry/step_agent_setup.py)) | Create the AI Foundry chat agent wired to the Knowledge Base via [MCP](https://modelcontextprotocol.io/introduction). **Best-effort**: transient platform errors are logged as warnings and the deployment continues. |
| 3 | | | `setup_workspace` ([`step_workspace_setup.py`](../infra/scripts/fabric/step_workspace_setup.py)) | Create or find the Fabric workspace, assign it to the capacity, and resume the capacity if paused. |
| 4 | | | `setup_administrators` ([`step_workspace_admins.py`](../infra/scripts/fabric/step_workspace_admins.py)) | Add [workspace administrators](https://learn.microsoft.com/fabric/get-started/roles-workspaces) using [Graph API](https://learn.microsoft.com/graph/overview) resolution with fallback. |
| 5 | | | `upload_installer` ([`step_notebook_installer.py`](../infra/scripts/fabric/step_notebook_installer.py)) | Upload [`fabric_solution_installer.ipynb`](../infra/fabric/deploy/fabric_solution_installer.ipynb), patched in-memory with the current git branch and `GITHUB_TOKEN` if set. |
| 6 | | | `run_installer` ([`step_notebook_installer.py`](../infra/scripts/fabric/step_notebook_installer.py)) | Execute the installer notebook as a Fabric job. The notebook uses [`fabric-launcher`](https://github.com/microsoft/fabric-launcher) to deploy items from [`src/fabric/fabric_workspace/`](../src/fabric/fabric_workspace/), then runs `pipeline_main` for data ingestion, deploys ontologies, and organizes folders. |

---

## Deployment Environment Setup

You can deploy the accelerator from any of the four environments below. Each prepares the same set of prerequisites — Azure Developer CLI, Python, Azure CLI, and access to your subscription — and then runs the common [Deployment Commands](#deployment-commands) below. Pick whichever option fits your workflow.

> **Common requirements for all options**
> - An **Azure subscription** with permissions to create resources
> - **Microsoft Fabric** enabled on your subscription ([register provider](https://learn.microsoft.com/azure/azure-resource-manager/management/resource-providers-and-types))
> - (Optional) A GitHub Personal Access Token with `repo` scope and `Contents: read` if you forked the repo as private — set with `azd env set GITHUB_TOKEN "ghp_..."` ([create one](https://github.com/settings/personal-access-tokens))

<details>
<summary><b>Option 1 · Local Deployment</b> — your own machine</summary>

Use this option to run the deployment from your local shell.

1. **Install prerequisites** on your host:
   - [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) (`azd`)
   - [Python 3.9+](https://www.python.org/downloads/)
   - [PowerShell 7+](https://learn.microsoft.com/powershell/scripting/install/installing-powershell) — required because [`azure.yaml`](../azure.yaml) hooks invoke [`infra/scripts/utils/Run-PythonScript.ps1`](../infra/scripts/utils/Run-PythonScript.ps1)
2. **Clone the repository** and `cd` into it:
   ```bash
   git clone https://github.com/microsoft/microsoft-iq-solution-accelerator.git
   cd microsoft-iq-solution-accelerator
   ```
3. Continue with the [Deployment Commands](#deployment-commands) below.

</details>

<details>
<summary><b>Option 2 · GitHub Codespaces</b> — zero-install browser environment</summary>

[GitHub Codespaces](https://github.com/features/codespaces) provisions a cloud dev container that already contains every tool needed by the accelerator (defined in [`.devcontainer/`](../.devcontainer/README.md)).

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/microsoft/microsoft-iq-solution-accelerator)

1. Click the **Open in GitHub Codespaces** badge above (or use **Code → Codespaces → Create codespace** on the repository page) to launch a codespace on the default branch. To target a fork or branch, replace `microsoft/microsoft-iq-solution-accelerator` in the URL with `<owner>/<repo>` and append `?ref=<branch>` if needed.
2. Wait for the codespace to finish building. The `postCreateCommand` runs [`post-create.sh`](../.devcontainer/post-create.sh) and [`setup_env.sh`](../.devcontainer/setup_env.sh) automatically — they install Python deps, `msodbcsql18`, dev tooling, and helpful aliases.
3. Continue with the [Deployment Commands](#deployment-commands) below — the repository is already cloned at the working directory. If `azd auth login` opens a browser window that fails to redirect back to the codespace, use `azd auth login --use-device-code`.

> See [`.devcontainer/README.md`](../.devcontainer/README.md) for the full list of pre-installed tools and extensions.

</details>

<details>
<summary><b>Option 3 · Dev Container (VS Code + Docker Desktop)</b> — local container, same image as Codespaces</summary>

Run the same dev container locally for an isolated, reproducible environment without polluting your host.

1. **Install prerequisites** on your host:
   - [Visual Studio Code](https://code.visualstudio.com/)
   - [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. **Clone the repository** and open it in VS Code:
   ```bash
   git clone https://github.com/microsoft/microsoft-iq-solution-accelerator.git
   code microsoft-iq-solution-accelerator
   ```
3. Run **Command Palette → *Dev Containers: Reopen in Container***. VS Code builds the image from [`.devcontainer/Dockerfile`](../.devcontainer/Dockerfile) and runs the post-create scripts.
4. Continue with the [Deployment Commands](#deployment-commands) below. Existing `azd` credentials from the host's `~/.azure` (or `%USERPROFILE%\.azure`) are bind-mounted into the container, so a previous `azd auth login` carries over.

> See [`.devcontainer/README.md`](../.devcontainer/README.md) for configuration details and troubleshooting.

</details>

<details>
<summary><b>Option 4 · GitHub Actions</b> — automated CI/CD deployment</summary>

The repository ships with [`.github/workflows/azure-dev.yml`](../.github/workflows/azure-dev.yml), which runs `azd up` end-to-end on `push` to a branch (and on `workflow_dispatch`) using **OIDC federated credentials** — no secrets stored.

1. **Configure a federated credential** in Microsoft Entra ID for your fork or this repository. See [Configure a federated identity credential](https://learn.microsoft.com/entra/workload-id/workload-identity-federation-config-app-trust-create#github-actions) and [`azd pipeline config`](https://learn.microsoft.com/azure/developer/azure-developer-cli/configure-devops-pipeline) (which can do this for you).
2. **Create a GitHub environment** named `miq-build` (referenced by the workflow's `environment: 'miq-build'` job) and add three repository **secrets**:
   - `AZURE_CLIENT_ID` — the app registration / managed identity client ID
   - `AZURE_TENANT_ID` — your Microsoft Entra tenant ID
   - `AZURE_SUBSCRIPTION_ID` — target subscription
3. (Optional) Adjust `AZURE_LOCATION` in the workflow `env:` block (default `westus3`) and any `azd env set …` lines for SKU, region, or model overrides.
4. **Trigger** the workflow by pushing to a branch matching the `paths:` filters (`infra/**`, `src/**`, `.github/workflows/azure-dev.yml`) or by running it manually from the **Actions** tab. The workflow:
   - Logs in via `azure/login@v2` and `azd auth login --federated-credential-provider github`
   - Runs Bicep static analysis and validation
   - Executes `azd up --no-prompt` (which itself triggers Phase 2)

> The same six post-provision steps described above run inside the workflow. You do **not** need to run the [Deployment Commands](#deployment-commands) section manually for this option — the workflow performs them on your behalf.

</details>

---

## Deployment Commands

### Prerequisites

These commands assume you have completed one of the [Deployment Environment Setup](#deployment-environment-setup) options above (Local, Codespaces, or Dev Container) and have a shell open in the repository root. For [Option 4 · GitHub Actions](#deployment-environment-setup), skip this section — the workflow runs these commands automatically.

### Deploy

Run the following commands in a single bash session:

```bash
# Authenticate with Azure Developer CLI (run only if not already logged in)
azd auth login

# (Optional) Provide a GitHub PAT if you forked the repo as private.
# The Fabric installer notebook pulls workspace items from GitHub.
azd env set GITHUB_TOKEN "ghp_..."   # optional

# (Optional) Override defaults — Fabric SKU, AI region, model selection, etc.
# See the "Optional Configuration Variables" section below for the full list.
# azd env set FABRIC_CAPACITY_SKU_NAME F4
# azd env set AZURE_AI_DEPLOYMENTS_LOCATION eastus

# Deploy the solution
# This will prompt you to select Azure subscription and region,
# then provision all infrastructure and run post-deployment scripts
azd up

# (Optional) View all deployment outputs
azd env get-values
```

> For fine-grained tuning of the deployment (Fabric capacity SKU, workspace name, AI deployment region, model selection, existing-resource reuse, etc.), set any of the variables documented in [Optional Configuration Variables](#optional-configuration-variables) **before** running `azd up`.

The entire deployment typically completes in **10–15 minutes**.

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
| | `FABRIC_WORKSPACE_ADMINISTRATORS` | Comma-separated additional workspace admins (UPNs and/or object IDs) | _(empty)_ | `azd env set FABRIC_WORKSPACE_ADMINISTRATORS "user@contoso.com,11111111-2222-3333-4444-555555555555"` |
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

After successful deployment, you will have a single Azure Resource Group containing the resources below, plus a Fabric workspace populated by the installer notebook.

### Azure Resources (Resource Group)

| Component | Purpose |
|---|---|
| **Fabric Capacity** (`{solution_suffix}-fabric-capacity` or your existing capacity) | Compute backing the Fabric workspace. Resumed automatically if paused. |
| **User-assigned Managed Identity** | Identity used by deployment scripts and Foundry connections to call Azure AI Search and Storage without secrets. |
| **Microsoft Foundry Hub & Project** | Container for AI agents, model deployments, knowledge bases, and connections. |
| **Azure OpenAI deployments** | Two model deployments inside the Foundry project: a chat completion model (default `gpt-4.1-mini`) and an embedding model (default `text-embedding-3-small`). |
| **Azure AI Search** | Vector + keyword search service. Backs the Foundry knowledge base; index name `{solution_suffix}-documents`. |
| **Azure Storage Account** | Blob storage for source documents. Container `{solution_suffix}-documents` is uploaded to by `setup_knowledge_base` and referenced by AI Search citations. |
| **Log Analytics workspace + Application Insights** | Diagnostic and monitoring sink for the Foundry project, AI Search, and the chat agent. Reused if `AZURE_EXISTING_LOG_ANALYTICS_WORKSPACE_ID` is set. |
| **Foundry connections** | Project connections wiring Foundry to AI Search, Blob Storage, and the Knowledge Base MCP endpoint (`{solution_suffix}-kb-mcp-connection`). |

**Access in the Azure portal**: open [portal.azure.com](https://portal.azure.com) → **Resource groups** → select the group named after your `azd` environment (the value of `AZURE_RESOURCE_GROUP`, shown by `azd env get-values`). Use the resource list to navigate to any individual resource. Diagnostic logs are available under **Monitoring → Logs** on the Foundry project, AI Search, and Storage resources.

### Fabric IQ Components

The installer notebook deploys workspace items from [`src/fabric/fabric_workspace/`](../src/fabric/fabric_workspace/) into the Fabric workspace:

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
- Open the [Microsoft Fabric portal](https://app.fabric.microsoft.com) and sign in with the same account used for `azd auth login`.
- Switch the experience to **Fabric Developer** (top-right) and select your workspace from the left sidebar (default name: `Microsoft IQ - {SOLUTION_SUFFIX}`).
- The lakehouse, notebooks, semantic models, ontologies, and data agents above appear under the workspace's items list — use the folder filters to narrow by type.
- Direct link template: `https://app.fabric.microsoft.com/groups/{workspace_id}?experience=fabric-developer` (the `workspace_id` is printed in the deployment summary and saved as `FABRIC_WORKSPACE_ID` in your `azd` environment).

### Microsoft Foundry Components

Sourced and named by [`install_microsoft_iq_solution.py`](../infra/scripts/install_microsoft_iq_solution.py) (steps `setup_knowledge_base` and `setup_agent`).

| Component | Default name | Purpose |
|---|---|---|
| **Search Index** | `{solution_suffix}-documents` | Azure AI Search index containing chunked PDFs from [`src/foundry/data/documents/`](../src/foundry/data/documents/) with embeddings for hybrid (vector + keyword) retrieval. Override with `AZURE_AI_SEARCH_INDEX`. |
| **Knowledge Source** | `{solution_suffix}-ks` | Foundry IQ pointer to the AI Search index. |
| **Knowledge Base** | `{solution_suffix}-kb` | Foundry IQ knowledge base with automatic query planning over the knowledge source. Used by the agent for grounded answers with citations. |
| **KB MCP project connection** | `{solution_suffix}-kb-mcp-connection` | Foundry connection that exposes the Knowledge Base to the agent through the [Model Context Protocol](https://modelcontextprotocol.io/introduction). Override with `KB_MCP_CONNECTION_NAME`. |
| **Chat Agent** | `ChatAgent` | AI Foundry agent wired to the Knowledge Base via the MCP tool above. Answers questions with document citations. |

#### Verify in the Foundry portal

Open [ai.azure.com](https://ai.azure.com) and sign in with the same account used for `azd auth login`. From the landing page, select your hub and then your project (the project name is stored as `AZURE_AI_PROJECT_NAME` in your `azd` environment; the endpoint is `AZURE_AI_AGENT_ENDPOINT`). Once inside the project, confirm:

1. **Knowledge Bases** → `{solution_suffix}-kb` exists, status is *Ready*, and it lists `{solution_suffix}-ks` as its source.
2. **Agents** → an agent named `ChatAgent` exists, its model matches `AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME` / `AZURE_CHAT_MODEL` (default `gpt-4.1-mini`), and the **Tools** panel shows the `{solution_suffix}-kb-mcp-connection` MCP tool attached.
3. **Connections** → the AI Search, Blob Storage, and KB MCP connections are all *Connected*.

> If `setup_agent` finished with a warning during deployment, this verification is the recommended way to check whether the agent was actually created. If `ChatAgent` is missing, simply re-run `azd up`.

**Test the agent from the CLI**:
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
- `AZURE_AI_AGENT_ENDPOINT` — Microsoft Foundry agent endpoint
- `AZURE_AI_SEARCH_ENDPOINT` — Search service endpoint
- `AZURE_STORAGE_BLOB_ENDPOINT` — Document storage endpoint
- `AZURE_FABRIC_CAPACITY_NAME` — Fabric capacity name
- `SOLUTION_NAME` / `SOLUTION_SUFFIX` — Your solution identifier and suffix used in resource names

### Next Steps

1. **Add your documents**: drop PDFs into [`src/foundry/data/documents/`](../src/foundry/data/documents/) and re-run the deployment to refresh the knowledge base:
   ```bash
   azd up
   ```
   This re-executes `setup_knowledge_base` (Step 1), which re-uploads PDFs to blob storage and re-indexes them.
2. **Explore the Fabric workspace**: open notebooks and run the data pipelines.
3. **Test the agent**: use the test script above, or chat with `ChatAgent` from the Foundry portal.
4. **View dashboards**: access the Power BI reports in the Fabric workspace.

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