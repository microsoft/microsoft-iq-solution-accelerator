# Copilot Studio Integration - Deployment Guide

This guide covers prerequisites, step-by-step deployment, customization, and troubleshooting for the Copilot Studio integration. See [README.md](./README.md) for an overview and [TestingGuide.md](./TestingGuide.md) for end-to-end QA testing.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Steps](#deployment-steps)
   - [Step 1: Import the Power Platform Solution](#step-1-import-the-power-platform-solution)
   - [Step 2: Configure Connections](#step-2-configure-connections)
   - [Step 3: Configure the Copilot Studio Agent](#step-3-configure-the-copilot-studio-agent)
   - [Step 4: Configure the Power Automate Flow](#step-4-configure-the-power-automate-flow)
   - [Step 5: Activate the Solution](#step-5-activate-the-solution)
3. [Customization and Extension](#customization-and-extension)
4. [Troubleshooting](#troubleshooting)
5. [References](#references)

---

## Prerequisites

### 1. Azure and Fabric Resources Deployed

The Fabric IQ and Foundry IQ components must be deployed first. Follow the [main Deployment Guide](../DeploymentGuide.md) to provision:

- ✅ Microsoft Fabric workspace with lakehouse, semantic models, and data agents
- ✅ Azure AI Foundry project with knowledge base and chat agent
- ✅ Azure AI Search with indexed documents
- ✅ OpenAI models (GPT-4 and embeddings)

### 2. Power Platform Environment

You need access to a [Power Platform environment](https://learn.microsoft.com/power-platform/admin/create-environment) with:

- **Copilot Studio** license ([licensing info](https://learn.microsoft.com/microsoft-copilot-studio/requirements-licensing))
- **Power Automate** license ([licensing info](https://learn.microsoft.com/power-platform/admin/pricing-billing-skus))
- **Permissions**: Environment Maker role or higher ([role info](https://learn.microsoft.com/power-platform/admin/database-security))

### 3. Service Endpoints and Credentials

Gather the following information from your deployed Azure resources:

| Component | Required Information | Where to Find It |
|---|---|---|
| **Fabric Data Agent** | Workspace ID, Agent ID, API endpoint | [Fabric Portal](https://app.fabric.microsoft.com) → Workspace → Data Agent |
| **Foundry Agent** | Project endpoint, Agent ID, API key | [Azure AI Foundry Portal](https://ai.azure.com) → Project → Deployments |
| **Azure AD App Registration** | Client ID, Client Secret, Tenant ID | [Azure Portal](https://portal.azure.com) → App Registrations (if using service principal auth) |

### 4. Email Account

- Access to an **Office 365 email account** or **Outlook** inbox that will receive triggering emails
- Permissions to create inbox rules or shared mailbox access

---

## Deployment Steps

### Step 1: Import the Power Platform Solution

The solution package is located at [`../../src/copilot/sln/3IQAccelerator_1_0_0_1_managed.zip`](../../src/copilot/sln/3IQAccelerator_1_0_0_1_managed.zip).

#### 1.1 Download the Solution File

1. Navigate to the repository folder: `src/copilot/sln/`
2. Download the file: `3IQAccelerator_1_0_0_1_managed.zip`
3. Save it to a local directory

#### 1.2 Import to Power Platform

1. **Navigate to Power Platform Admin Center**
   - Go to [Power Platform admin center](https://admin.powerplatform.microsoft.com/)
   - Select your target **Environment**

2. **Access Solutions**
   - In the left navigation, click **Solutions**
   - Or navigate directly to [https://make.powerapps.com](https://make.powerapps.com) → **Solutions**

3. **Import the Solution**
   - Click **Import solution** button at the top
   - Click **Browse** and select the downloaded ZIP file: `3IQAccelerator_1_0_0_1_managed.zip`
   - Click **Next**

4. **Review Import Settings**
   - Review the solution details displayed
   - Click **Next** to proceed

5. **Configure Connections** (Initial Setup)
   - The import wizard will prompt you to establish connections for:
     - **Office 365 Outlook** (for email triggers and sending)
     - **Fabric Data Agent** (custom connector - to be configured)
     - **Foundry Agent** (custom connector - to be configured)
   - For now, click **Skip** or create basic connections - we'll configure these properly in Step 2
   - Click **Import**

6. **Wait for Import Completion**
   - The import process may take 3-5 minutes
   - Once complete, you'll see a success message: "Solution imported successfully"

> **Reference**: [Import solutions in Power Platform](https://learn.microsoft.com/power-platform/alm/import-solution)

---

### Step 2: Configure Connections

After importing the solution, configure connections to external services.

#### 2.1 Configure Office 365 Outlook Connection

1. Go to [Power Automate portal](https://make.powerautomate.com) → **Data** → **Connections**
2. Click **+ New connection** → search for "Office 365 Outlook" → **Create**
3. Sign in with your Office 365 account and grant permissions when prompted

> **Reference**: [Office 365 Outlook connector documentation](https://learn.microsoft.com/connectors/office365/)

#### 2.2 Configure Fabric Data Agent Connection

**Option A: Using HTTP with Azure AD Connector** (Recommended)

1. In **Connections**, click **+ New connection** → search for "HTTP with Azure AD"
2. Configure Azure AD Authentication:
   - **Base Resource URL**: `https://api.fabric.microsoft.com`
   - **Azure AD Resource URI**: `https://api.fabric.microsoft.com`
   - Click **Sign in** and authenticate with your Azure AD account

**Option B: Using Custom Connector** (Advanced)

Create a custom connector following the [Fabric REST API documentation](https://learn.microsoft.com/rest/api/fabric/articles/using-fabric-apis).

> **Reference**: [HTTP with Azure AD connector](https://learn.microsoft.com/connectors/webcontents/)

#### 2.3 Configure Foundry Agent Connection

1. In **Connections**, click **+ New connection** → search for "HTTP" → **Create**
2. Retrieve your Foundry Project endpoint and API key from [Azure AI Foundry Portal](https://ai.azure.com):
   - Go to your Project → **Settings** → **Keys and endpoints**
   - Copy the **Project endpoint** and **Primary key**

> **Reference**: [Azure AI Foundry API authentication](https://learn.microsoft.com/azure/ai-studio/how-to/develop/sdk-overview)

#### 2.4 Update Solution Connection References

1. Navigate to **Solutions** in Power Platform → click **3IQ Accelerator**
2. Click **Connection References** tab
3. For each connection reference, click **...** → **Edit** → select the connection you created → **Save**

> **Reference**: [Connection references in solutions](https://learn.microsoft.com/power-platform/alm/conn-ref-env-variables-build-deploy)

---

### Step 3: Configure the Copilot Studio Agent

#### 3.1 Open the Agent

1. Go to [Copilot Studio portal](https://copilotstudio.microsoft.com) → select your **Environment**
2. Click **Copilots** → find and open the **3IQ Accelerator Agent**

#### 3.2 Configure Topics and Variables

1. Click **Topics** in the left menu to review pre-configured topics:
   - **Email Request Handler** - Processes incoming email requests
   - **Data Query Handler** - Routes queries to Fabric Data Agent
   - **Knowledge Search Handler** - Routes searches to Foundry Agent

2. Update environment-specific variables in each topic as needed:
   - `FabricWorkspaceId`: Your Fabric workspace ID
   - `FabricAgentId`: Your Fabric Data Agent ID
   - `FoundryEndpoint`: Your Azure AI Foundry project endpoint
   - `FoundryAgentId`: Your Foundry agent/deployment ID

#### 3.3 Configure Agent Authentication

1. In the Agent editor, click **Settings** (gear icon) → **Security** → **Authentication**

2. **For Fabric (Azure AD)**:
   - **Authentication type**: OAuth 2.0
   - **Authority**: `https://login.microsoftonline.com/common`
   - **Scopes**: `https://api.fabric.microsoft.com/.default`

3. **For Foundry (API Key)**:
   - **Authentication type**: API Key
   - **Header name**: `api-key`
   - **Key value**: Your Foundry API key (from Step 2.3)

> **Reference**: [Configure copilot authentication](https://learn.microsoft.com/microsoft-copilot-studio/configuration-authentication)

#### 3.4 Test the Agent

1. Click **Test your copilot** in the upper right
2. Try: "What data sources are available?" and "Search for supplier information in the knowledge base"
3. Verify the agent responds and check for connection errors in the test panel

> **Reference**: [Test your copilot](https://learn.microsoft.com/microsoft-copilot-studio/authoring-test-bot)

---

### Step 4: Configure the Power Automate Flow

#### 4.1 Open the Flow

1. Go to [Power Automate portal](https://make.powerautomate.com) → **Solutions** → **3IQ Accelerator**
2. Click on the flow: **3IQ Email Trigger Flow**

The flow contains these key steps: **Trigger** (new email) → **Parse Email** → **Invoke Agent** → **Send Response**

#### 4.2 Configure Email Trigger

1. Click on the trigger step: **When a new email arrives**
2. Configure:
   - **Folder**: Select the inbox folder to monitor (e.g., "Inbox" or a dedicated "3IQ Requests" folder)
   - **Subject Filter** (optional): e.g., "3IQ Request" to only trigger on specific emails
   - **Include Attachments**: Set to "No" unless processing attachments

> **Reference**: [Office 365 Outlook trigger documentation](https://learn.microsoft.com/connectors/office365/#when-a-new-email-arrives-(v3))

#### 4.3 Configure Agent Invocation

1. Locate the **Invoke Copilot** or **Ask a question** action
2. Set:
   - **Environment**: Your Power Platform environment
   - **Copilot**: 3IQ Accelerator Agent
   - `Question`: `@{triggerOutputs()?['body/body']}`
   - `ConversationId`: `@{triggerOutputs()?['body/internetMessageId']}`

#### 4.4 Configure Response Action

1. Locate the **Send an email (V2)** or **Reply to email (V3)** action
2. Set:
   - **To**: `@{triggerOutputs()?['body/from']}`
   - **Subject**: `RE: @{triggerOutputs()?['body/subject']}`
   - **Body**:
     ```html
     <p>Here's the information you requested:</p>
     <p>@{outputs('Invoke_Copilot')?['body/responseText']}</p>
     <br>
     <p><i>Powered by Microsoft IQ Solution Accelerator</i></p>
     ```

#### 4.5 Add Error Handling (Recommended)

1. Click **...** on the response action → **Configure run after** → select **has failed**, **has timed out**, **is skipped**
2. Add a parallel branch to send error notification emails on failure conditions

> **Reference**: [Error handling in Power Automate](https://learn.microsoft.com/power-automate/error-handling)

#### 4.6 Save and Test

1. Click **Save**, then **Test** → **Manually**
2. Send a test email to the monitored inbox and monitor execution in real-time

> **Reference**: [Test cloud flows](https://learn.microsoft.com/power-automate/test-flow)

---

### Step 5: Activate the Solution

#### 5.1 Turn On the Flow

- In the flow editor, ensure the toggle at the top is set to **On**
- Or from the Solutions view: click **...** on the flow → **Turn on**

#### 5.2 Publish the Agent

1. In Copilot Studio, open the **3IQ Accelerator Agent**
2. Click **Publish** in the upper right → **Publish**
3. Wait for publishing to complete (1-2 minutes)

> **Reference**: [Publish your copilot](https://learn.microsoft.com/microsoft-copilot-studio/publication-fundamentals-publish-channels)

#### 5.3 Grant Permissions

- **Agent**: In Copilot Studio → **Settings** → **Security** → **Access** → add users or security groups
- **Flow**: In Power Automate, open the flow → **Share** → add co-owners as needed

> **Reference**: [Share your copilot](https://learn.microsoft.com/microsoft-copilot-studio/admin-share-bots)

---

## Customization and Extension

### Customize Agent Behavior

#### Update Agent Instructions

1. In Copilot Studio, navigate to **Settings** → **AI capabilities** → **Instructions**
2. Modify the system instructions to change agent personality or behavior. Examples:
   ```
   - Always respond in a professional, concise manner
   - Prioritize data from the last 30 days unless specified otherwise
   - When uncertain, clearly state confidence level
   - Always provide data source citations
   ```

> **Reference**: [Configure copilot instructions](https://learn.microsoft.com/microsoft-copilot-studio/advanced-generative-actions#configure-the-instructions-for-your-copilot)

#### Add New Topics

1. Click **Topics** → **+ Add** → **Topic** → **From blank**
2. Create topics for specific business scenarios (supply chain alerts, financial variance analysis, etc.)
3. Link topics to custom Power Automate flows for complex workflows

### Extend with Additional Channels

#### Microsoft Teams

1. In Copilot Studio, click **Channels** → **Microsoft Teams** → **Turn on Teams**
2. Follow prompts to add the agent to Teams

> **Reference**: [Configure Microsoft Teams channel](https://learn.microsoft.com/microsoft-copilot-studio/publication-add-bot-to-microsoft-teams)

#### Custom Website

1. Click **Channels** → **Custom website** → copy the embed code
2. Add to your internal portal or website

> **Reference**: [Configure custom website channel](https://learn.microsoft.com/microsoft-copilot-studio/publication-connect-bot-to-web-channels)

### Add Custom Actions

1. In Power Automate, create a new flow with trigger: **When Power Virtual Agents calls a flow**
2. Add custom logic and return a response to the agent
3. In Copilot Studio, navigate to **Actions** → **+ Add an action** → select the flow and define input/output parameters

> **Reference**: [Add actions to copilot](https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow)

### Integrate with Power Apps

1. Build a Canvas or Model-driven Power App
2. Add the **Power Virtual Agents** connector
3. Use actions to send queries and display responses, or embed the agent chat control directly

> **Reference**: [Use copilot in Power Apps](https://learn.microsoft.com/power-apps/maker/canvas-apps/add-ai-copilot)

---

## Troubleshooting

### Flow Not Triggering on Email

- Verify the flow is turned **On** in Power Automate
- Check that the email folder and subject filter match the trigger configuration
- Re-authenticate the Office 365 Outlook connection: **Connections** → find the connection → **Edit** → **Re-authenticate**
- Check if the mailbox is full or has conflicting inbox rules

### Agent Returns Generic Error

- Test the agent independently in the Copilot Studio test panel
- Verify API endpoints and keys are current (Fabric workspace ID, Foundry endpoint URL and API key)
- Review agent **Topics** for hardcoded values that need updating
- Check Azure AI Foundry logs for failed requests

### Fabric Data Agent Not Returning Data

- Confirm the workspace ID in the agent configuration matches your deployed Fabric workspace
- Verify the user or service principal has **Member** or higher access in the workspace (**Workspace settings** → **Manage access**)
- Test the data agent directly in [Fabric Portal](https://app.fabric.microsoft.com) before invoking from Copilot

### Foundry Agent Search Returns No Results

- Verify documents are uploaded to Azure Storage (check the blob container)
- Confirm the Azure AI Search index exists and contains documents: Azure Portal → AI Search resource → **Search explorer**
- Re-run knowledge base indexing if needed (see [Foundry deployment steps](../DeploymentGuide.md#microsoft-foundry-components))

### Flow Times Out or Runs Slowly

- Ensure Fabric capacity is running (not paused)
- Configure HTTP actions with explicit timeouts (e.g., 30 seconds) and retry policies
- Consider an async pattern: send an acknowledgment email immediately, run the agent query in the background, then send results in a follow-up

### Getting Help

- **Power Platform Community**: [https://powerusers.microsoft.com/](https://powerusers.microsoft.com/)
- **Copilot Studio Documentation**: [https://learn.microsoft.com/microsoft-copilot-studio/](https://learn.microsoft.com/microsoft-copilot-studio/)
- **Azure AI Foundry Support**: [https://learn.microsoft.com/azure/ai-studio/](https://learn.microsoft.com/azure/ai-studio/)
- **Microsoft Fabric Community**: [https://community.fabric.microsoft.com/](https://community.fabric.microsoft.com/)

---

## References

### Power Platform & Copilot Studio

- [Microsoft Copilot Studio Documentation](https://learn.microsoft.com/microsoft-copilot-studio/)
- [Copilot Studio Licensing and Requirements](https://learn.microsoft.com/microsoft-copilot-studio/requirements-licensing)
- [Create and Configure Copilots](https://learn.microsoft.com/microsoft-copilot-studio/authoring-first-bot)
- [Configure Copilot Authentication](https://learn.microsoft.com/microsoft-copilot-studio/configuration-authentication)
- [Add Actions to Copilots](https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow)
- [Publish Your Copilot](https://learn.microsoft.com/microsoft-copilot-studio/publication-fundamentals-publish-channels)
- [Monitor Copilot Performance](https://learn.microsoft.com/microsoft-copilot-studio/analytics-overview)

### Power Automate

- [Power Automate Documentation](https://learn.microsoft.com/power-automate/)
- [Office 365 Outlook Connector](https://learn.microsoft.com/connectors/office365/)
- [HTTP with Azure AD Connector](https://learn.microsoft.com/connectors/webcontents/)
- [Error Handling in Flows](https://learn.microsoft.com/power-automate/error-handling)
- [Test Cloud Flows](https://learn.microsoft.com/power-automate/test-flow)

### Power Platform Solutions

- [Solution Concepts in Power Platform](https://learn.microsoft.com/power-platform/alm/solution-concepts-alm)
- [Import Solutions](https://learn.microsoft.com/power-platform/alm/import-solution)
- [Connection References](https://learn.microsoft.com/power-platform/alm/conn-ref-env-variables-build-deploy)
- [Application Lifecycle Management (ALM)](https://learn.microsoft.com/power-platform/alm/)

### Microsoft Fabric

- [Microsoft Fabric Documentation](https://learn.microsoft.com/fabric/)
- [Fabric REST API Reference](https://learn.microsoft.com/rest/api/fabric/)
- [Data Agents in Fabric](https://learn.microsoft.com/fabric/data-science/ai-services/data-agent-overview)
- [Fabric Workspace Roles](https://learn.microsoft.com/fabric/get-started/roles-workspaces)

### Azure AI Foundry

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Create AI Agents](https://learn.microsoft.com/azure/ai-studio/how-to/develop/create-agent)
- [Knowledge Bases](https://learn.microsoft.com/azure/ai-foundry/concepts/knowledge-bases)
- [Azure AI Search Integration](https://learn.microsoft.com/azure/search/search-what-is-azure-search)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)

### Authentication & Security

- [Azure Active Directory Authentication](https://learn.microsoft.com/azure/active-directory/fundamentals/)
- [Managed Identities for Azure Resources](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview)
- [API Key Authentication Best Practices](https://learn.microsoft.com/azure/security/fundamentals/key-management)

### Related Documentation

- [Main Deployment Guide](../DeploymentGuide.md) - Deploy Fabric and Foundry components
- [Fabric Data Agent README](../fabric/fabric_data_agent/README.md) - Configure and customize data agents
- [Technical Architecture](../TechnicalArchitecture.md) - Overall solution architecture
- [Solution README](../../README.md) - Solution overview and quick start
