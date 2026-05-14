# Testing Guide

This guide provides instructions for QA testers to verify the end-to-end functionality of the Microsoft IQ Solution Accelerator from a user's perspective. The focus is on testing the golden path: sending an email that triggers the agent to orchestrate responses from both Fabric IQ (data platform) and Foundry IQ (knowledge base), then receiving synthesized recommendations in Microsoft Teams.

---

## Table of Contents

1. [Resource Review Portals](#resource-review-portals)
2. [Adding the Copilot Studio Agent to Teams](#adding-the-copilot-studio-agent-to-teams)
3. [Golden Path Testing Flow](#golden-path-testing-flow)

---

## Resource Review Portals

Before testing, familiarize yourself with the deployed resources by visiting these portals:

### Azure Portal
- **URL**: [https://portal.azure.com](https://portal.azure.com)
- **What to Review**: Resource group containing Azure AI Foundry Hub, Azure AI Search, Azure Storage, Azure OpenAI Service, and Microsoft Fabric Capacity

### Azure AI Foundry Portal
- **URL**: [https://ai.azure.com](https://ai.azure.com)
- **What to Review**: Project with knowledge base, deployed models, and chat agent

### Microsoft Fabric Portal
- **URL**: [https://app.fabric.microsoft.com](https://app.fabric.microsoft.com)
- **What to Review**: Workspace with lakehouse, notebooks, semantic models, and data agents

### Copilot Studio
- **URL**: [https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)
- **What to Review**: The 3IQ Accelerator Agent and its configured topics

### Power Automate
- **URL**: [https://make.powerautomate.com](https://make.powerautomate.com)
- **What to Review**: The 3IQ Email Trigger Flow that monitors for incoming emails

---

## Adding the Copilot Studio Agent to Teams

You need to add the agent to Microsoft Teams to receive responses from the email-triggered workflow.

### Installation Methods

**Option 1: Direct Link**
- Get the Teams app installation link from your administrator (format: `https://teams.microsoft.com/l/app/[APP-ID]`)
- Click the link and Teams will open
- Click **Add** to install the agent

**Option 2: From Copilot Studio**
- In [Copilot Studio](https://copilotstudio.microsoft.com), open the 3IQ Accelerator Agent
- Navigate to **Channels** → **Microsoft Teams** → **Availability options**
- Copy the Teams app link and share with testers

After installation, open Teams and find the agent in your Chat list to verify it's ready.

---

## Golden Path Testing Flow

The golden path tests the complete workflow: an email triggers the Power Automate flow, which invokes the Copilot Studio agent. The agent orchestrates queries to both Fabric (for data) and Foundry (for knowledge base documents), synthesizes a response, and posts it to Teams.

### Step 1: Prepare Your Environment

1. **Open Microsoft Teams** with the agent chat visible
2. **Open your email client** (Outlook/Office 365) that's monitored by the flow  
3. **Open Power Automate** (optional) at [make.powerautomate.com](https://make.powerautomate.com) to monitor the flow run history

### Step 2: Send a Test Email

Send an email to trigger the agent. Use one of these example scenarios that test both data retrieval (Fabric) and knowledge base search (Foundry):

#### Example 1: Supply Chain Disruption

**Subject**: `Urgent: Supplier Delivery Delay Concern`

**Body**:
```
Hi Team,

I just received notification that our primary camping tent supplier, 
Mountain Peak Manufacturing, is experiencing production delays due to 
material shortages. This could impact our inventory levels significantly.

Can you provide:
1. Current inventory levels for all tent products from this supplier
2. Our alternative supplier options based on our supplier qualification policy
3. Recommended actions to mitigate supply chain risk

This is urgent as we're heading into peak season.

Thanks,
[Your Name]
```

#### Example 2: Inventory Risk Assessment

**Subject**: `Inventory Risk Check - Camping Gear`

**Body**:
```
Hello,

We're planning our Q2 purchasing strategy and need to assess current 
inventory risk across our camping gear product line.

Please provide:
- Current stock levels for camping tents and sleeping bags
- Sales trends for the past 30 days
- Any supplier-related risks based on our supply chain policies
- Recommendations for reorder quantities

Looking forward to the analysis.

Best regards,
[Your Name]
```

#### Example 3: Product Quality Issue

**Subject**: `Customer Complaint - Product Quality Investigation`

**Body**:
```
Team,

We've received multiple customer complaints about defective zippers 
on the "Alpine Explorer" tent model (SKU: TENT-ALP-001).

I need to investigate:
1. How many units of this product are currently in stock?
2. Which supplier/batch does this inventory come from?
3. What is our product quality escalation policy?
4. What are the steps to initiate a supplier quality review?

Please provide this information so we can take appropriate action.

Thanks,
[Your Name]
```

### Step 3: Monitor the Flow

After sending the email:
- Within 1-2 minutes, a new flow run should appear in Power Automate's run history (if monitoring)
- Typical execution time: 30 seconds to 2 minutes
- Status should progress from **Running** to **Succeeded**

### Step 4: Review Response in Teams

Within 1-3 minutes of sending the email, you should receive a message from the agent in Teams. The response should include:

1. **Acknowledgment** of your specific concern
2. **Data from Fabric** - inventory levels, sales data, product information
3. **Knowledge from Foundry** - policy excerpts with document citations
4. **Synthesized recommendations** - actionable next steps combining data and policy

### Step 5: Test Conversational Follow-ups

Continue the conversation in Teams to test context retention:

- "Can you show me inventory levels for just the sleeping bag products?"
- "What is our policy for expedited supplier approvals?"
- "Can you explain more about the risk mitigation options you mentioned?"
- "Based on current inventory and our reorder policy, when should we place the next order?"

The agent should maintain context from previous messages and provide relevant, coherent responses.

