# Copilot Studio Integration - Deployment Guide

This guide covers deploying and configuring the Copilot Studio integration. See [README.md](./README.md) for an overview and [TestingGuide.md](./TestingGuide.md) for end-to-end QA testing.

---

## Step 1: Import the Solution

The solution package is located at `src/copilot/sln/MicrosoftIQAccelerator` in this repository.

Import it into your Power Platform environment following the standard solution import process:
[Import a solution with your agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export#import-the-solution-with-your-agent)

At a high level:
1. Navigate to [make.powerapps.com](https://make.powerapps.com) and select your environment
2. Go to **Solutions** → **Import solution**
3. Upload latest `MicrosoftIQAccelerator*.zip` and follow the import wizard

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

---

## Step 3: Configure the Email Trigger

Once connections are set, configure the Power Automate flow to monitor the correct inbox:

1. Open **Solutions** → **Microsoft IQ Accelerator** → find the **Email Trigger Flow**
2. Edit the **When a new email arrives** trigger
3. Set the **Folder** to the inbox or folder you want to monitor
4. Optionally add a **Subject Filter** to limit which emails trigger the flow (e.g., `IQ Request`)
5. Save

---

## Step 4: Publish the Agent

1. Open [Copilot Studio](https://copilotstudio.microsoft.com) and select your environment
2. Open the **Microsoft IQ Accelerator** agent
3. Click **Publish** and wait for publishing to complete (1-2 minutes)
4. Configure Teams as a channel: **Channels** → **Microsoft Teams** → **Turn on Teams**

The solution is now active and ready to test. See the [Testing Guide](./TestingGuide.md) for the golden path QA flow.
