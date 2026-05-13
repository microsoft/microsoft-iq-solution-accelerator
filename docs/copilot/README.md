# Microsoft IQ Solution Accelerator - Copilot Studio Integration

This document provides comprehensive guidance for deploying and configuring the **Copilot Studio Agent** as the orchestration layer for the Microsoft IQ Solution Accelerator. The Copilot Studio Agent serves as the intelligent ingress point that unifies all three IQ components: **Fabric IQ** (data platform), **Foundry IQ** (knowledge base), and **Work IQ** (workflow orchestration).

---

## Table of Contents

1. [Solution Overview](#solution-overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Deployment Steps](#deployment-steps)
   - [Step 1: Import the Power Platform Solution](#step-1-import-the-power-platform-solution)
   - [Step 2: Configure Connections](#step-2-configure-connections)
   - [Step 3: Configure the Copilot Studio Agent](#step-3-configure-the-copilot-studio-agent)
   - [Step 4: Configure the Power Automate Flow](#step-4-configure-the-power-automate-flow)
   - [Step 5: Activate the Solution](#step-5-activate-the-solution)
5. [Testing the Solution](#testing-the-solution)
6. [Customization and Extension](#customization-and-extension)
7. [Troubleshooting](#troubleshooting)
8. [References](#references)

---

## Solution Overview

The Copilot Studio integration creates an intelligent workflow that:

1. **Monitors for incoming emails** via a Power Automate flow with email triggers
2. **Routes requests to the Copilot Studio Agent** which orchestrates the response
3. **Queries Fabric Data Agent** to access real-time datasets, semantic models, and ontologies for operational data insights
4. **Searches Foundry Agent** to retrieve relevant information from the knowledge base of business documents
5. **Synthesizes responses** combining structured data and unstructured knowledge
6. **Delivers actionable insights** back through the workflow

This solution demonstrates the power of unified intelligence, connecting disparate data sources and AI agents into a cohesive decision-support system.

### Key Components

- **Copilot Studio Agent**: The central orchestrator that understands user intent and coordinates responses
- **Power Automate Flow**: Email-triggered workflow that initiates the agent and manages communication
- **Fabric Data Agent Connection**: Integration with Microsoft Fabric for accessing data lakehouses, semantic models, and ontologies
- **Foundry Agent Connection**: Integration with Azure AI Foundry for knowledge base search and retrieval
- **Power Platform Solution**: Pre-configured package containing the agent, flows, and connections

---

## Architecture

The following diagram illustrates the architecture of the Copilot Studio integration:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Email Trigger (Outlook)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Power Automate Flow                            │
│  • Parse email content                                           │
│  • Extract request parameters                                    │
│  • Invoke Copilot Studio Agent                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Copilot Studio Agent                            │
│  • Understand user intent                                        │
│  • Orchestrate multi-agent workflow                              │
│  • Synthesize responses                                          │
└──────────────┬──────────────────────────────┬───────────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────┐    ┌────────────────────────────────┐
│  Fabric Data Agent       │    │  Foundry Agent                 │
│  • Lakehouse queries     │    │  • Knowledge base search       │
│  • Semantic model data   │    │  • Document retrieval          │
│  • Ontology reasoning    │    │  • Citation generation         │
│  • Real-time analytics   │    │  • RAG (Retrieval Augmented)   │
└──────────────────────────┘    └────────────────────────────────┘
```

### Data Flow

1. **Email Arrival**: User sends email to monitored inbox with a business question
2. **Flow Trigger**: Power Automate flow triggers on email receipt
3. **Agent Invocation**: Flow extracts content and invokes Copilot Studio Agent
4. **Intent Analysis**: Agent analyzes the request and determines required data sources
5. **Parallel Queries**:
   - If structured data needed → Query Fabric Data Agent
   - If document knowledge needed → Query Foundry Agent
6. **Response Synthesis**: Agent combines results from both sources
7. **Response Delivery**: Formatted response sent back via email or Teams message

---

## Prerequisites

Before deploying the Copilot Studio solution, ensure you have completed the following:

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

> **Note**: See [Configure Authentication](#configure-authentication) section for detailed guidance on retrieving these values.

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
   - You'll see a progress indicator
   - Once complete, you'll see a success message: "Solution imported successfully"

> **Reference**: [Import solutions in Power Platform](https://learn.microsoft.com/power-platform/alm/import-solution)

---

### Step 2: Configure Connections

After importing the solution, you need to configure connections to external services.

#### 2.1 Configure Office 365 Outlook Connection

1. **Navigate to Connections**
   - Go to [Power Automate portal](https://make.powerautomate.com)
   - Click **Data** → **Connections** in the left navigation

2. **Create Office 365 Outlook Connection**
   - Click **+ New connection**
   - Search for "Office 365 Outlook"
   - Click **Office 365 Outlook** connector
   - Click **Create**
   - Sign in with your Office 365 account
   - Grant permissions when prompted

> **Reference**: [Office 365 Outlook connector documentation](https://learn.microsoft.com/connectors/office365/)

#### 2.2 Configure Fabric Data Agent Connection

The Fabric Data Agent requires a custom connector or HTTP connector with authentication.

**Option A: Using HTTP with Azure AD Connector** (Recommended)

1. **Create HTTP with Azure AD Connection**
   - In **Connections**, click **+ New connection**
   - Search for "HTTP with Azure AD"
   - Click **HTTP with Azure AD** connector

2. **Configure Azure AD Authentication**
   - **Base Resource URL**: `https://api.fabric.microsoft.com`
   - **Azure AD Resource URI**: `https://api.fabric.microsoft.com`
   - Click **Sign in**
   - Authenticate with your Azure AD account

3. **Note Connection Details**
   - After creation, note the connection name - you'll reference this in the flow

**Option B: Using Custom Connector** (Advanced)

If you need more control, create a custom connector following the [Fabric REST API documentation](https://learn.microsoft.com/rest/api/fabric/articles/using-fabric-apis).

> **Reference**: [HTTP with Azure AD connector](https://learn.microsoft.com/connectors/webcontents/)

#### 2.3 Configure Foundry Agent Connection

The Foundry Agent can be accessed via HTTP calls to the Azure AI Foundry endpoint.

1. **Create HTTP Connection**
   - In **Connections**, click **+ New connection**
   - Search for "HTTP"
   - Click **HTTP** connector
   - Click **Create**

2. **Note Authentication Details**
   - You'll configure authentication details in the flow itself
   - Retrieve your Foundry Project endpoint and API key from [Azure AI Foundry Portal](https://ai.azure.com)
   - Go to your Project → **Settings** → **Keys and endpoints**
   - Copy the **Project endpoint** and **Primary key**

> **Reference**: [Azure AI Foundry API authentication](https://learn.microsoft.com/azure/ai-studio/how-to/develop/sdk-overview)

#### 2.4 Update Solution Connections

1. **Open the Solution**
   - Navigate to **Solutions** in Power Platform
   - Click on **3IQ Accelerator** solution

2. **Update Connection References**
   - Click **Connection References** tab
   - For each connection reference:
     - Click the **ellipsis (...)** → **Edit**
     - Select the connection you created in the above steps
     - Click **Save**

> **Reference**: [Connection references in solutions](https://learn.microsoft.com/power-platform/alm/conn-ref-env-variables-build-deploy)

---

### Step 3: Configure the Copilot Studio Agent

The Copilot Studio Agent needs to be configured with the endpoints and authentication for both Fabric and Foundry agents.

#### 3.1 Open the Agent in Copilot Studio

1. **Navigate to Copilot Studio**
   - Go to [Copilot Studio portal](https://copilotstudio.microsoft.com)
   - Select your **Environment**

2. **Open the 3IQ Agent**
   - Click **Copilots** in the left navigation
   - Find and click on the **3IQ Accelerator Agent** (imported from solution)

#### 3.2 Configure Topics and Actions

1. **Review Topics**
   - Click **Topics** in the left menu
   - Review the pre-configured topics:
     - **Email Request Handler** - Processes incoming email requests
     - **Data Query Handler** - Routes queries to Fabric Data Agent
     - **Knowledge Search Handler** - Routes searches to Foundry Agent

2. **Update Variables** (if needed)
   - Each topic contains variables for endpoints and configurations
   - Click on a topic to edit
   - Update variables with your environment-specific values:
     - `FabricWorkspaceId`: Your Fabric workspace ID
     - `FabricAgentId`: Your Fabric Data Agent ID
     - `FoundryEndpoint`: Your Azure AI Foundry project endpoint
     - `FoundryAgentId`: Your Foundry agent/deployment ID

#### 3.3 Configure Agent Authentication

1. **Add Authentication Configuration**
   - In the Agent editor, click **Settings** (gear icon)
   - Navigate to **Security** → **Authentication**

2. **Configure for Fabric (Azure AD)**
   - Add an authentication profile for Fabric API:
     - **Authentication type**: OAuth 2.0
     - **Authority**: `https://login.microsoftonline.com/common`
     - **Scopes**: `https://api.fabric.microsoft.com/.default`

3. **Configure for Foundry (API Key)**
   - Add a second authentication profile for Foundry:
     - **Authentication type**: API Key
     - **Header name**: `api-key`
     - **Key value**: Your Foundry API key (from Step 2.3)

> **Reference**: 
> - [Configure copilot authentication](https://learn.microsoft.com/microsoft-copilot-studio/configuration-authentication)
> - [Use authentication with actions](https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow-authentication)

#### 3.4 Test the Agent

1. **Open Test Chat**
   - Click **Test your copilot** button in the upper right
   - The test panel will appear on the right side

2. **Test Basic Responses**
   - Try: "What data sources are available?"
   - Try: "Search for supplier information in the knowledge base"

3. **Verify Connections**
   - Ensure the agent responds appropriately
   - Check for connection errors in the test panel
   - Review conversation logs in the debugger

> **Reference**: [Test your copilot](https://learn.microsoft.com/microsoft-copilot-studio/authoring-test-bot)

---

### Step 4: Configure the Power Automate Flow

The Power Automate flow orchestrates the email trigger and agent invocation.

#### 4.1 Open the Flow

1. **Navigate to Power Automate**
   - Go to [Power Automate portal](https://make.powerautomate.com)
   - Click **Solutions** → **3IQ Accelerator**
   - Click on the flow: **3IQ Email Trigger Flow**

2. **Review Flow Structure**
   The flow contains these key steps:
   - **Trigger**: "When a new email arrives (V3)"
   - **Parse Email**: Extract subject, body, sender
   - **Invoke Agent**: Call Copilot Studio Agent
   - **Send Response**: Reply to original email

#### 4.2 Configure Email Trigger

1. **Edit Trigger Settings**
   - Click on the trigger step: **When a new email arrives**
   - Configure:
     - **Folder**: Select the inbox folder to monitor (e.g., "Inbox" or create a dedicated "3IQ Requests" folder)
     - **Subject Filter** (optional): Add filter like "3IQ Request" to only trigger on specific emails
     - **Include Attachments**: Set to "No" (or "Yes" if you want to process attachments)

2. **Set Up Inbox Routing** (Optional)
   - Create an Outlook rule to route specific emails to the monitored folder
   - This prevents the agent from triggering on every email

> **Reference**: [Office 365 Outlook trigger documentation](https://learn.microsoft.com/connectors/office365/#when-a-new-email-arrives-(v3))

#### 4.3 Configure Agent Invocation

1. **Locate Agent Action**
   - Find the action: **Invoke Copilot** or **Ask a question** (Copilot Studio connector)

2. **Update Agent Configuration**
   - **Environment**: Select your Power Platform environment
   - **Copilot**: Select **3IQ Accelerator Agent**
   - **Input Parameters**:
     - `Question`: Use dynamic content from email body: `@{triggerOutputs()?['body/body']}`
     - `ConversationId`: `@{triggerOutputs()?['body/internetMessageId']}` (to track conversations)

#### 4.4 Configure Response Action

1. **Locate Response Action**
   - Find the action: **Send an email (V2)** or **Reply to email (V3)**

2. **Configure Response Settings**
   - **To**: Use dynamic content: `@{triggerOutputs()?['body/from']}`
   - **Subject**: `RE: @{triggerOutputs()?['body/subject']}`
   - **Body**: Use the agent's response output:
     ```html
     <p>Here's the information you requested:</p>
     <p>@{outputs('Invoke_Copilot')?['body/responseText']}</p>
     <br>
     <p><i>Powered by Microsoft IQ Solution Accelerator</i></p>
     ```

#### 4.5 Add Error Handling (Recommended)

1. **Configure Run After Settings**
   - Click **...** on response action → **Configure run after**
   - Select **has failed**, **has timed out**, **is skipped**
   - This ensures error messages are sent back

2. **Add Parallel Error Response Branch**
   - Add a parallel action to send error emails
   - Configure to only run on failure conditions

> **Reference**: [Error handling in Power Automate](https://learn.microsoft.com/power-automate/error-handling)

#### 4.6 Save and Test

1. **Save the Flow**
   - Click **Save** in the upper right
   - Wait for validation to complete

2. **Test the Flow**
   - Click **Test** button
   - Select **Manually**
   - Send a test email to the monitored inbox
   - Monitor the flow execution in real-time

> **Reference**: [Test cloud flows](https://learn.microsoft.com/power-automate/test-flow)

---

### Step 5: Activate the Solution

#### 5.1 Turn On the Flow

1. **Activate the Flow**
   - In the flow editor, ensure the toggle at the top is set to **On**
   - Or from the Solutions view:
     - Click **...** on the flow → **Turn on**

#### 5.2 Publish the Copilot

1. **Publish the Agent**
   - Go back to Copilot Studio
   - Open the **3IQ Accelerator Agent**
   - Click **Publish** button in the upper right
   - Select **Publish**
   - Wait for publishing to complete (1-2 minutes)

> **Reference**: [Publish your copilot](https://learn.microsoft.com/microsoft-copilot-studio/publication-fundamentals-publish-channels)

#### 5.3 Grant Permissions (if needed)

1. **Share the Agent**
   - In Copilot Studio, click **Settings** → **Security** → **Access**
   - Add users or security groups who should have access
   - Set appropriate permission levels

2. **Share the Flow**
   - In Power Automate, open the flow
   - Click **Share** button
   - Add co-owners if needed

> **Reference**: [Share your copilot](https://learn.microsoft.com/microsoft-copilot-studio/admin-share-bots)

---

## Testing the Solution

### End-to-End Test Scenarios

#### Test 1: Data Query via Fabric Agent

1. **Send Test Email**
   - **To**: Your monitored inbox email address
   - **Subject**: `3IQ Request: Sales Data Query`
   - **Body**: 
     ```
     What were the total sales for the last quarter? Please break down by region.
     ```

2. **Expected Flow**:
   - Flow triggers on email receipt
   - Agent analyzes request and identifies need for structured data
   - Agent queries Fabric Data Agent for sales data
   - Agent receives data and formats response
   - Reply email sent with sales breakdown

3. **Verify Results**:
   - Check email for response within 1-2 minutes
   - Response should include structured data from Fabric lakehouse
   - Review flow run history for successful execution

#### Test 2: Knowledge Search via Foundry Agent

1. **Send Test Email**
   - **To**: Your monitored inbox
   - **Subject**: `3IQ Request: Supplier Policy`
   - **Body**: 
     ```
     What is our company policy for qualifying new suppliers?
     ```

2. **Expected Flow**:
   - Flow triggers on email receipt
   - Agent identifies need for document knowledge
   - Agent queries Foundry Agent knowledge base
   - Agent receives relevant document excerpts with citations
   - Reply email sent with policy information and source references

3. **Verify Results**:
   - Response should include document excerpts
   - Should contain citations to source documents
   - Check Foundry agent logs for search activity

#### Test 3: Combined Query (Both Agents)

1. **Send Test Email**
   - **To**: Your monitored inbox
   - **Subject**: `3IQ Request: Supplier Risk Assessment`
   - **Body**: 
     ```
     What is the inventory risk for our top supplier based on current stock levels 
     and our supplier evaluation policy?
     ```

2. **Expected Flow**:
   - Agent identifies need for both data and knowledge
   - Parallel queries to both Fabric and Foundry agents
   - Synthesized response combining current data with policy guidelines

3. **Verify Results**:
   - Response should include both data metrics and policy references
   - Should demonstrate unified intelligence across all components

### Monitoring and Logs

1. **Flow Run History**
   - Navigate to **Power Automate** → **My flows** → **3IQ Email Trigger Flow**
   - Click **Run history** tab
   - Review success/failure status and execution details

2. **Copilot Studio Analytics**
   - Open **Copilot Studio** → **3IQ Accelerator Agent**
   - Click **Analytics** tab
   - Review metrics: sessions, resolution rate, escalations

3. **Agent Logs**
   - Fabric Agent: [Fabric Portal](https://app.fabric.microsoft.com) → Workspace → Data Agent → Activity logs
   - Foundry Agent: [Azure AI Foundry](https://ai.azure.com) → Project → Tracing & Monitoring

> **Reference**: [Monitor copilot performance](https://learn.microsoft.com/microsoft-copilot-studio/analytics-overview)

---

## Customization and Extension

### Customize Agent Behavior

#### Update Agent Instructions

1. Open the agent in Copilot Studio
2. Navigate to **Settings** → **AI capabilities** → **Instructions**
3. Modify the system instructions to change agent personality or behavior
4. Example additions:
   ```
   - Always respond in a professional, concise manner
   - Prioritize data from the last 30 days unless specified otherwise
   - When uncertain, clearly state confidence level
   - Always provide data source citations
   ```

> **Reference**: [Configure copilot instructions](https://learn.microsoft.com/microsoft-copilot-studio/advanced-generative-actions#configure-the-instructions-for-your-copilot)

#### Add New Topics

1. Click **Topics** → **+ Add** → **Topic** → **From blank**
2. Create topics for specific business scenarios:
   - Supply chain disruption alerts
   - Financial variance analysis
   - Inventory optimization recommendations
3. Link topics to custom Power Automate flows for complex workflows

### Extend with Additional Channels

Deploy the agent to additional channels beyond email:

#### Microsoft Teams Integration

1. In Copilot Studio, click **Channels**
2. Select **Microsoft Teams**
3. Click **Turn on Teams**
4. Follow prompts to add the agent to Teams
5. Users can now chat with the agent directly in Teams

> **Reference**: [Configure Microsoft Teams channel](https://learn.microsoft.com/microsoft-copilot-studio/publication-add-bot-to-microsoft-teams)

#### Power Virtual Agents Website

1. Click **Channels** → **Custom website**
2. Copy the provided embed code
3. Add to your internal portal or website
4. Users can access the agent via web chat widget

> **Reference**: [Configure custom website channel](https://learn.microsoft.com/microsoft-copilot-studio/publication-connect-bot-to-web-channels)

### Add Custom Actions

Extend the agent with custom Power Automate flows:

1. **Create Custom Flow**
   - In Power Automate, create a new flow
   - Use trigger: **When Power Virtual Agents calls a flow**
   - Add your custom logic (e.g., call external APIs, write to databases)
   - Return response to agent

2. **Register Action in Agent**
   - In Copilot Studio, navigate to **Actions** → **+ Add an action**
   - Select your custom flow
   - Define input/output parameters
   - Call the action from topics

> **Reference**: [Add actions to copilot](https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow)

### Integrate with Power Apps

Create Power Apps that invoke the agent:

1. Build a Power App (Canvas or Model-driven)
2. Add **Power Virtual Agents** connector
3. Use actions to:
   - Send user queries to agent
   - Display agent responses in app UI
   - Embed agent chat control directly in app

> **Reference**: [Use copilot in Power Apps](https://learn.microsoft.com/power-apps/maker/canvas-apps/add-ai-copilot)

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Flow Not Triggering on Email

**Symptoms**: Email arrives but flow doesn't execute

**Possible Causes**:
- Flow is turned off
- Email doesn't match folder or subject filter
- Connection expired or invalid

**Solutions**:
1. Verify flow is turned **On** in Power Automate
2. Check trigger settings match your email criteria
3. Re-authenticate Office 365 Outlook connection:
   - Go to **Connections** → Find Office 365 Outlook → **Edit** → **Re-authenticate**
4. Check if mailbox is full or has rules that interfere

#### Issue 2: Agent Returns Generic Error

**Symptoms**: Agent responds with "I encountered an error" or similar

**Possible Causes**:
- Agent connection to Fabric or Foundry failed
- Authentication issues
- API endpoint misconfigured

**Solutions**:
1. Test agent independently in Copilot Studio test panel
2. Check authentication configuration in agent settings
3. Verify API endpoints and keys are current:
   - Fabric workspace ID and agent ID correct
   - Foundry endpoint URL and API key valid
4. Review agent **Topics** for hardcoded values that need updating
5. Check Azure AI Foundry logs for failed requests

#### Issue 3: Fabric Data Agent Not Returning Data

**Symptoms**: Agent response indicates no data found or connection timeout

**Possible Causes**:
- Data agent not deployed in Fabric
- Workspace ID incorrect
- Permissions missing

**Solutions**:
1. Verify Fabric Data Agent is deployed:
   - Go to [Fabric Portal](https://app.fabric.microsoft.com)
   - Navigate to workspace → Check for data agent
2. Confirm workspace ID matches configuration
3. Verify user/service principal has access to workspace:
   - Workspace settings → **Manage access**
   - Add user as **Member** or higher
4. Test data agent directly in Fabric portal before invoking from Copilot

#### Issue 4: Foundry Agent Search Returns No Results

**Symptoms**: Knowledge base queries return empty or irrelevant results

**Possible Causes**:
- Knowledge base not indexed
- Documents not uploaded
- Search index configuration issue

**Solutions**:
1. Verify documents are uploaded to Azure Storage:
   - Check storage account → blob container
2. Confirm Azure AI Search index exists and has documents:
   - Go to Azure Portal → AI Search resource → **Search explorer**
   - Run test query
3. Re-run knowledge base indexing:
   - See [Foundry deployment steps](../DeploymentGuide.md#microsoft-foundry-components)
4. Check Foundry agent query logs for search terms used

#### Issue 5: Flow Times Out or Runs Slowly

**Symptoms**: Flow execution takes > 2 minutes or times out

**Possible Causes**:
- Foundry query timeout
- Large result sets
- Network latency

**Solutions**:
1. Add timeout handling in flow:
   - Configure HTTP actions with explicit timeout (e.g., 30 seconds)
   - Add retry policies
2. Optimize agent queries:
   - Limit result set sizes
   - Use filters to narrow searches
3. Consider async pattern:
   - Send acknowledgment email immediately
   - Run agent query in background
   - Send results in follow-up email

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

---

## Next Steps

After successfully deploying the Copilot Studio integration:

1. **Pilot with User Group**: Test with a small group of business users
2. **Gather Feedback**: Collect insights on response quality and coverage
3. **Refine Agent Instructions**: Tune prompts and topics based on real usage
4. **Expand Channels**: Deploy to Teams, web portals, or other channels
5. **Add Custom Actions**: Build flows for specific business processes
6. **Monitor Performance**: Use analytics to track adoption and effectiveness
7. **Scale Gradually**: Expand to additional departments or use cases

For questions or support, refer to the [Troubleshooting](#troubleshooting) section or consult the [References](#references) for detailed documentation.

---

*Last updated: May 2026*