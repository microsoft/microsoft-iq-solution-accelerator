# Deployment Guide

Deploy the **Microsoft IQ Solution Accelerator** using Azure Developer CLI (`azd`) and the repo's automated deployment artifacts. This guide walks you through deploying the Fabric IQ, Foundry IQ, and Work IQ components.

## Key Sections

| Section | Description |
|---|---|
| [Overview](#overview) | High-level deployment architecture and workflow |
| [Step 1: Prerequisites & Setup](#step-1-prerequisites--setup) | Azure, Fabric, and software requirements |
| [Step 2: Choose Your Deployment Environment](#step-2-choose-your-deployment-environment) | Local, Codespaces, Dev Container, Cloud Shell, or GitHub Actions |
| [Step 3: Configure Deployment Settings (Optional)](#step-3-configure-deployment-settings-optional) | Customize deployment variables and reuse existing resources |
| [Step 4: Deploy the Solution](#step-4-deploy-the-solution) | Run `azd up` and validate deployment |
| [Step 5: Post-Deployment Configuration](#step-5-post-deployment-configuration) | Work IQ import and verification steps |
| [Step 6: Deployment Results](#step-6-deployment-results) | Verify Azure and Fabric resources |
| [Step 7: Clean Up (Optional)](#step-7-clean-up-optional) | Remove deployed resources safely |
| [Known Issues and Troubleshooting](#known-issues-and-troubleshooting) | Common errors and resolutions |
| [Next Steps](#next-steps) | Further guides and resources |
| [Need Help?](#need-help) | Support and repo guidance |

---

## Overview

The Microsoft IQ Solution Accelerator consists of three components:

- **Foundry IQ** – Provisions Azure AI Foundry resources, including Agents, knowledge bases, and search indexes for intelligent document-based question answering.
- **Fabric IQ** – Deploys Fabric artifacts, including lakehouses, notebooks, semantic models, pipelines, and data agents for a unified data foundation.
- **Work IQ** – A Copilot Studio email-triggered agent that orchestrates Fabric IQ and Foundry IQ. It is deployed manually after `azd up` by importing the Power Platform solution from `src/copilot/sln`.

The azd up deployment is fully automated, idempotent, and deploys both Foundry IQ and Fabric IQ. Work IQ is configured separately as a post-deployment step.

---


## Step 1: Prerequisites & Setup

Before starting the deployment, ensure the following prerequisites are met.

### 1.1 Azure Account Requirements

Ensure you have access to an [Azure subscription](https://azure.microsoft.com/free/) with the following permissions:

| Permission | Level | Purpose |
|-----------|-------|---------|
| **Contributor** | Subscription/Resource Group | Deploy Bicep templates and create Azure resources |
| **User Access Administrator** | Subscription/Resource Group | Configure role-based access control (RBAC) |
| **Resource Provider Registration** | Subscription | Register the required Azure resource providers: `Microsoft.Fabric`, `Microsoft.EventHub`, and `Microsoft.Storage`. |


### 1.2 Microsoft Fabric Requirements

Your organization must have the following setup:

| Requirement | Details |
|-------------|---------|
| **Fabric License** | [Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/admin/fabric-switch) must be enabled in your organization |
| **Fabric Capacity** | Dedicated capacity available for your deployments (or deployment will create one) |
| **Workspace Creation** | Permissions to create new Fabric workspaces |
| **REST API Access** | If using Service Principals or Managed Identities, [enable the tenant setting](https://learn.microsoft.com/rest/api/fabric/articles/identity-support) for "Service principals and managed identities support on Fabric REST API" |

### 1.3 Fabric tenant settings

Before deployment, enable these [Fabric tenant settings](https://learn.microsoft.com/en-us/fabric/iq/ontology/overview-tenant-settings) in the Fabric Admin Portal:

- **Ontology (preview)**
- **Graph (preview)**
- **Copilot and Azure OpenAI Service**

If Fabric Admin permissions are not available, ask your tenant administrator to enable these settings. Settings may take several minutes to propagate.

### 1.4 Identity options for deployment

Choose the identity that best matches your deployment scenario:

| Identity | Recommended for |
|----------|------------------|
| **User account** | Interactive deployments from your local machine or GitHub Codespaces. |
| **Service principal (federated identity)** | Automated CI/CD deployments using GitHub Actions with OpenID Connect (OIDC). |
| **Managed identity** | Azure-hosted deployment environments that support managed identities. |

> [Note]
> For GitHub Actions, configure a Microsoft Entra ID federated credential and a GitHub environment with the required Azure credentials before running the workflow.

### 1.5 Software requirements

**Note:** Skip this section if using GitHub Codespaces, VS Code Dev Container, or Azure Cloud Shell—all tools are pre-installed in these environments.

Install the following tools on your local machine:

| Tool | Version | Installation |
|------|---------|--------------|
| **Python** | 3.9 or later | [Download from python.org](https://www.python.org/downloads/) |
| **Azure CLI** | Latest | [Install Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) |
| **Azure Developer CLI (azd)** | Latest | [Install azd](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) |
| **Bicep CLI** | 0.33.0 or later | [Install Bicep](https://learn.microsoft.com/azure/azure-resource-manager/bicep/install) |
| **Git** | Latest | [Download from git-scm.com](https://git-scm.com/downloads) |


---

## Step 2: Choose Your Deployment Environment

Use the environment that best matches your workflow.

| Environment | Setup Required | Notes |
|-------------|----------------|-------|
| **[GitHub Codespaces](#option-a-github-codespaces)** | GitHub account | Cloud development environment |
| **[Visual Studio Code Dev Container](#option-b-vs-code-dev-container)** | Docker Desktop + VS Code | Containerized consistency |
| **[Local Machine](#option-c-local-machine)** | Install [software requirements](#14-software-requirements) | Most flexible, requires local setup |
| **[GitHub Actions](#option-d-github-actions)** | Azure service principal | Federated identity, automated deployment |

### Option A: GitHub Codespaces

1. Go to the [Microsoft IQ Solution accelerator repository in GitHub Codespaces](https://github.com/codespaces/new/microsoft/microsoft-iq-solution-accelerator)
2. Follow the instructions on screen to create a new codespace with default setup.
3. Wait for the environment to initialize (2-3 minutes)
4.. All tools are pre-installed; proceed to [Step 4: Deploy](#step-4-deploy-the-solution)


### Option B: VS Code Dev Container

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
6. Click "Reopen in Container" when prompted
7. All tools are pre-installed; proceed to [Step 4: Deploy](#step-4-deploy-the-solution)


### Option C: Local Machine

1. Install the software requirements from [Step 1.4](#15-software-requirements).
2. Clone the repository:

```bash
git clone https://github.com/microsoft/microsoft-iq-solution-accelerator.git
cd microsoft-iq-solution-accelerator
```

3. Continue to [Step 4: Deploy the Solution](#step-4-deploy-the-solution).

### Option D: GitHub Actions

**Automated deployment using GitHub Actions with OpenID Connect (OIDC).**

1. Complete the [GitHub Actions prerequisites](#15-software-requirements), including:
   - Configure a Microsoft Entra ID federated credential.
   - Create the `miq-build` GitHub environment with the required Azure values.
2. (Optional) Update the workflow configuration (for example, `AZURE_LOCATION` or other deployment settings) in `.github/workflows/azure-dev.yml`.
3. Trigger the workflow by:
   - Pushing changes to a branch that matches the workflow path filters, or
   - Running the workflow manually from the **Actions** tab.
4. The workflow automatically authenticates to Azure using OIDC, validates the infrastructure, and runs `azd up` to deploy the solution.

> [!NOTE]
> You do not need to perform the manual deployment steps. The GitHub Actions workflow completes the deployment automatically.

---

## Step 3: Configure Deployment Settings (Optional)

Before deploying, optionally override defaults with `azd env set`.

### Common configuration variables

```bash
azd env set FABRIC_CAPACITY_SKU_NAME F4
# REQUIRED: set the AI deployment region to your preferred Azure region (no default)
# Example: azd env set AZURE_AI_DEPLOYMENTS_LOCATION eastus
azd env set AZURE_AI_DEPLOYMENTS_LOCATION <your-region>
azd env set AZURE_OPENAI_DEPLOYMENT_MODEL gpt-5-mini
azd env set AZURE_OPENAI_MODEL_VERSION 2025-04-14
azd env set AZURE_OPENAI_EMBEDDING_MODEL text-embedding-3-small
azd env set AZURE_SEARCH_SERVICE_LOCATION eastus
```

### Fabric workspace configuration

```bash
azd env set FABRIC_WORKSPACE_NAME "My IQ Workspace"
azd env set FABRIC_WORKSPACE_ADMINISTRATORS "user@contoso.com,11111111-2222-3333-444444444444"
```

### Reuse existing resources

If you already have existing resources in your tenant, set one or more of these:

```bash
azd env set AZURE_EXISTING_FABRIC_CAPACITY_NAME "my-existing-fabric-capacity"
azd env set FABRIC_WORKSPACE_NAME "My Existing Workspace"
azd env set AZURE_SEARCH_SERVICE_LOCATION "eastus"
```

> Note: The accelerator can reuse existing Fabric capacity or workspace resources if they already exist.

### Work IQ / Copilot configuration

This repository includes the Work IQ solution in `src/copilot/sln`. `azd up` deploys the Fabric IQ and Foundry components, but Work IQ requires manual import after deployment.

### Configuration summary

- `FABRIC_CAPACITY_SKU_NAME` — Fabric capacity SKU.
- `AZURE_AI_DEPLOYMENTS_LOCATION` — Azure AI deployment region.
- `AZURE_OPENAI_DEPLOYMENT_MODEL` — OpenAI GPT deployment model.
- `AZURE_OPENAI_EMBEDDING_MODEL` — Embedding model.
- `FABRIC_WORKSPACE_NAME` — Fabric workspace name.
- `FABRIC_WORKSPACE_ADMINISTRATORS` — Additional workspace admins.
- `AZURE_EXISTING_FABRIC_CAPACITY_NAME` — Reuse capacity.

---

## Step 4: Deploy the Solution

### 4.1 Authenticate

```bash
azd auth login
az login
```

If you are deploying to a specific tenant, use `--tenant-id` with `azd auth login`.

### 4.2 Set environment variables (optional)

If you want to customize the deployment, set values before running `azd up`.

```bash
azd env set FABRIC_CAPACITY_SKU_NAME F4
## REQUIRED: set `AZURE_AI_DEPLOYMENTS_LOCATION` to your preferred region (no default)
# Example: azd env set AZURE_AI_DEPLOYMENTS_LOCATION eastus
azd env set AZURE_AI_DEPLOYMENTS_LOCATION <your-region>
azd env set FABRIC_WORKSPACE_NAME "My IQ Workspace"
```

### 4.3 Run deployment

```bash
azd up
```

The deployment will prompt for:

1. Environment name
2. Azure subscription
3. Azure resource group

The deployment typically completes in **10–15 minutes**.

### 4.4 Verify deployment outputs

After deployment completes, run:

```bash
azd env get-values
```

This displays key outputs such as the Azure resource group, Fabric workspace name, and Foundry endpoint values.

### 4.5 Re-run deployment

The deployment is idempotent. Rerun with:

```bash
azd up
```

Existing resources are updated instead of recreated.

---

## Step 5: Post-Deployment Configuration

`azd up` provisions Fabric IQ and Microsoft Foundry components. After successful deployment, complete the Work IQ integration manually.

### 5.1 Import Work IQ solution

1. Open Power Platform and import the solution ZIP from `src/copilot/sln`.
2. Configure the required connections for Copilot Studio, Microsoft Teams, Outlook, Fabric Data Agent, and Foundry Agent.
3. Use the `AZURE_AI_AGENT_ENDPOINT` and other output values from `azd env get-values` when configuring connections.
4. Publish the agent in Copilot Studio.

For a step-by-step guide, see `docs/copilot/DeploymentGuide.md`.

### 5.2 Validate Fabric IQ and Foundry

Verify:

- Fabric workspace and artifacts are present in `app.fabric.microsoft.com`
- Microsoft Foundry agent endpoints are available
- Data ingestion, search, and knowledge base components are configured

### 5.3 Optional verification

- Open Fabric workspace and check the deployed Fabric IQ workspace components.
- Confirm Microsoft Foundry knowledge base and agent setup.
- Validate that the Work IQ Power Platform solution is published successfully.

---

## Step 6: Deployment Results

### Azure resources

The deployment creates or reuses the following Azure resources:

- Resource Group
- Fabric Capacity
- Azure AI/OpenAI deployment resources
- Azure Search service location
- Microsoft Foundry-related service endpoints

### Fabric IQ components

The Fabric workspace contains:

- Workspace
- Semantic models and datasets
- Data agent configuration artifacts
- Notebooks and environment definitions for Fabric IQ

### Microsoft Foundry components

The deployment also provisions:

- Foundry agent service endpoints
- Knowledge base search integration
- Agent runtime configuration used by Work IQ

### Output values

Important output values are available from `azd env get-values` and are used for:

- Copilot Studio connection setup
- Foundry agent endpoint configuration
- Fabric workspace access

---

## Step 7: Clean Up (Optional)

When you no longer need the deployment, remove resources safely:

```bash
cd microsoft-iq-solution-accelerator
azd down --force --purge
```

This command removes deployed Azure and Fabric resources created by the deployment while preserving your local source code.

If `azd down` fails, remove the resource group manually from the Azure Portal.

---

## Known Issues and Troubleshooting

### Fabric tenant access issues

If the Fabric API returns a 403 or requests are denied by inbound policy, verify:

- Tenant Fabric settings are enabled
- Your account has access to the Fabric workspace
- Network or proxy restrictions are not blocking `api.fabric.microsoft.com`

### Deployment permission issues

If deployment fails due to authorization:

- Confirm your identity has Contributor access on the target subscription or resource group
- Confirm service principal or federated identity is allowed to use Fabric REST API
- Ensure required Azure resource providers are registered

### Work IQ import issues

If manual Work IQ import fails:

- Confirm Power Platform connectors are authorized
- Use the outputs from `azd env get-values` for endpoint configuration
- Verify the Copilot solution version in `src/copilot/sln`

---

## Next Steps

After deployment, explore these guides:

- `docs/TechnicalArchitecture.md`
- `docs/FAQs.md`
- `docs/copilot/README.md`
- `docs/copilot/TestingGuide.md`

---

## Need Help?

- Open an issue in the repository if you encounter bugs.
- Review `CONTRIBUTING.md` for contribution guidance.
- See `SUPPORT.md` for support and escalation paths.
