# Microsoft IQ Solution Accelerator - Copilot Studio Integration

The **Copilot Studio Agent** serves as the intelligent ingress point that unifies all three IQ components: **Fabric IQ** (data platform), **Foundry IQ** (knowledge base), and **Work IQ** (workflow orchestration).

| Document | Description |
|---|---|
| [Deployment Guide](./DeploymentGuide.md) | Prerequisites, step-by-step setup, customization, and troubleshooting |
| [Testing Guide](./TestingGuide.md) | Golden path QA testing flow and test scenarios |

---

## Table of Contents

1. [Solution Overview](#solution-overview)
2. [Architecture](#architecture)

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

### Work IQ

[Work IQ](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq) is the intelligence layer that personalizes Microsoft 365 Copilot for users and organizations.

- Connects the Copilot Studio Agent to **Microsoft Graph** for the organization
- Grants access to Microsoft 365 tenant data: Outlook emails, Teams messages, SharePoint content, and collaboration signals
- Enables the agent to **draft and send emails** on behalf of users as part of its workflow orchestration

---

## Architecture

The following diagram illustrates the architecture of the Copilot Studio integration:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Email Trigger (Outlook)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Power Automate Flow                           │
│  • Parse email content                                          │
│  • Extract request parameters                                   │
│  • Invoke Copilot Studio Agent                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Copilot Studio Agent                           │
│  • Understand user intent                                       │
│  • Orchestrate multi-agent workflow                             │
│  • Synthesize responses                                         │
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

## Deployment

Before deploying the Copilot Studio solution, see the [Deployment Guide](./DeploymentGuide.md) for full prerequisites and step-by-step setup instructions.

---