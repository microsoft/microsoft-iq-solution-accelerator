# Copilot Studio Integration - Deployment Guide
 
This guide covers deploying and configuring the Copilot Studio integration for **Microsoft IQ Solution Accelerator**. See [README.md](./README.md) for an overview and [TestingGuide.md](./TestingGuide.md) for end-to-end QA testing.
 
---
## Prerequisites
 
* Power Platform environment with **Dataverse** enabled.
* **System Administrator** role on the Power Platform environment deploying the solution.
* Active **Microsoft Copilot Studio User License** should be assigned.
* End-user access to **Dataverse**.
* Access to **Microsoft Teams** and **Microsoft Outlook**.
* Access to the **Fabric Data Agent** and **Foundry Agent**, which is deployed as part of this solution. See [README.md](./README.md)
 
---
 
## Step 1: Import the Solution
 
The solution package is located in the [solution folder](../../src/copilot/sln) in this repository.
 
Import it into your Power Platform environment following the standard solution import process:
[Import a solution with your agent](Export and import agents using solutions - Microsoft Copilot Studio | Microsoft Learn)
 
At a high level:
1. Navigate to [make.powerapps.com](https://make.powerapps.com) and select your environment
2. Go to **Solutions** → **Import solution**
3. Import the zip file from the [solution folder](../../src/copilot/sln) in the environment [provisioned earlier](#prerequisites).
3. Click Next.
4. Click '**sign in'** for any connections that prompt to do so. Refer [Step 2](#step-2-configure-connections) for details.
6. After importing has completed, click **Publish all customizations** in the top menu. Wait for publishing to complete.
7. When the import is complete, the solution will be available in the environment.
 
---
 
## Step 2: Configure Connections
 
During import, each connection must be signed into and authorized.
 
| Connection | Notes |
|---|---|
| **Work IQ** | Sign in with your organizational account |
| **Microsoft Teams** | Sign in with your organizational account |
| **Copilot Studio** | Sign in with your organizational account |
| **Office 365 Outlook** | Sign in with the account whose inbox will be monitored |
| **Fabric Data Agent** | Authenticate with Entra (`https://api.fabric.microsoft.com`) |
| **Foundry Agent** | Authenticate and provide the Azure AI Foundry project endpoint from the prerequisite deployment  |
 
The Copilot agent also depends on two environment-specific external agents. Re-link them in Copilot Studio before you publish.
 
---
 
## Step 3: Configure the Email Trigger
 
Once connections are set, configure the Power Automate flow to monitor the correct inbox:
 
1. Open **Solutions** → **Microsoft IQ Accelerator** → find the **Email Trigger Flow**
2. Edit the **When a new email arrives** trigger
3. Set the **Folder** to the inbox or folder you want to monitor
4. Optionally add a **Subject Filter** to limit which emails trigger the flow (e.g., `IQ Request`)
5. Save
 
---
 
## Step 4: Add the External Agents in Copilot Studio
 
After import, add the Fabric and Foundry agents again in Copilot Studio. Use Fabric for data questions and Foundry for document questions. If they do not appear yet, finish deploying Fabric and Foundry first, then return to Copilot Studio and refresh the agent list.
 
### 4.1 Add the Foundry Chat Agent
 
1. Open [Copilot Studio](https://copilotstudio.microsoft.com) and select your environment.
2. Open the **Microsoft IQ Accelerator** agent.
3. Navigate to **Agents** from the top pane and then select + Add to add agents.
4. Choose **Connect to an external agent**.
5. Select **Microsoft Foundry**.
6. Authenticate with Microsoft Entra.
7. Provide the Azure AI Foundry project endpoint configured during the Foundry deployment. The article uses the format `https://<project-resource>.services.ai.azure.com/api/projects/<project-name>`.
8. Save the connection and confirm the Foundry agent appears in the connected-agent list.
 
 
### 4.2 Add the Fabric Data Agent
 
1. Stay in the same **Microsoft IQ Accelerator** agent.
2. Navigate to **Agents** from the top pane and then select + Add to add agents.
3. Select **Connect to an external agent** and select **Microsoft Fabric** from the dropdown.
4. If there's already a connection between Microsoft Fabric and the Microsoft IQ agent, you can select **Next** and move to next step. Otherwise, select the dropdown and select Create new connection to establish a connection between Microsoft Fabric and Copilot Studio.
5. Pick the published **Fabric Data Agent** that belongs to this solution.
6. Save the connection and make sure the Fabric agent now shows up in the list of connected agents.
 
---
 
## Step 5: Verify Work IQ connections
 
### 5.1 Verify the MCP tools are connected and enabled
 
1. Open the **Tools** tab.
2. Click the **Model Context Protocol** filter chip.
3. Confirm that you can see these three tools:
 
    | Tool name | Type | Available to | Trigger |
    |---|---|---|---|
    | Work IQ Copilot (Preview) | Model Context Protocol | Microsoft IQ Agent | By agent |
    | Work IQ Mail (Preview) | Model Context Protocol | Microsoft IQ Agent | By agent |
    | Work IQ User (Preview) | Model Context Protocol | Microsoft IQ Agent | By agent |
 
4. For each tool, confirm that:
    - The **Enabled** toggle is set to **On**.
    - The **Errors** column is empty.
    - The **Blocked** column is empty.
    - The **Last refreshed** indicator reads **Last refreshed now** after you refresh the list.
 
## Step 6: Publish the Agent
 
1. Open [Copilot Studio](https://copilotstudio.microsoft.com) and select your environment
2. Open the **Microsoft IQ Accelerator** agent
3. Click **Publish** and wait for publishing to complete (1-2 minutes)
4. Configure Teams as a channel: **Channels** → **Microsoft Teams** → **Turn on Teams**
 
The solution is now active and ready to test. See the [Testing Guide](./TestingGuide.md) for the golden path QA flow.