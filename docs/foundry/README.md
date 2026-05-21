# Foundry IQ — Intelligent Document Q&A

## Overview

Foundry IQ is the **document question-answering** component of the Microsoft IQ Solution Accelerator. It enables users to upload PDF documents and interact with an AI-powered agent that answers questions with direct references to the exact pages and sources.

### Key Capabilities

- **Natural language Q&A** — ask questions about your uploaded documents in plain English
- **Source citations** — every answer includes page numbers and links to the original documents
- **Intelligent search** — finds relevant information even when the exact words from the document are not used
- **Summarization and comparison** — synthesizes information across multiple documents
- **Chart generation** — creates visual representations from data found in your documents

## Sample Questions

Once your documents are uploaded, try asking things like:

- *"What are the qualification criteria for new suppliers?"*
- *"Summarize the key steps in the supplier onboarding process"*
- *"What performance metrics are used for supplier monitoring?"*
- *"Compare the requirements between different procedures"*

For more examples organized by category, see **[Sample Questions](./sample_questions.md)**.

## Getting Started

1. **Deploy** — Run `azd up` to set up all the required cloud services automatically.
2. **Add your documents** — Place your PDF files in the [`src/foundry/data/documents/`](../../src/foundry/data/documents/) folder and re-run `azd up`.
3. **Open the agent** — Go to [ai.azure.com](https://ai.azure.com) → select your hub → select your project → **Agents** → `ChatAgent`.
4. **Start asking questions** — Begin with *"What documents are available?"* to see what's in your knowledge base.

> For the full deployment walkthrough, see the [top-level Deployment Guide](../DeploymentGuide.md).

## Managing Your Documents

| What you want to do | How to do it |
|---|---|
| **Add new documents** | Place PDF files in the [`src/foundry/data/documents/`](../../src/foundry/data/documents/) folder |
| **Update the knowledge base** | Re-run `azd up` — this processes and indexes your new documents |
| **Check that indexing worked** | Go to [ai.azure.com](https://ai.azure.com) → **Knowledge Bases** → verify status shows *Ready* |
| **Test the agent from command line** | Run `python infra/scripts/foundry/test_agent.py` from the repository root |

### How citations work

Every answer the agent gives includes:
- **Page numbers** pointing to the exact page in the original PDF
- **Direct links** to the source documents stored in the cloud
- **Source attribution** showing which document(s) the answer came from

## Tips for Best Results

- **Start with discovery** — ask *"What documents are available?"* to understand what's in your knowledge base.
- **Be specific** — ask about particular policies, procedures, or topics rather than broad questions.
- **Reference your documents** — mention document names or types for more precise answers.
- **Ask for citations** — the agent provides source links; ask for them explicitly if not shown.
- **Build on answers** — ask follow-up questions to dive deeper into a topic.

---

## How It Works (Technical Details)

This section explains the underlying architecture for developers and technical stakeholders.

### Architecture Overview

Foundry IQ is built on [Azure AI Foundry](https://ai.azure.com) and uses these components:

| Component | What it does |
|---|---|
| **Azure AI Foundry Hub & Project** | Central platform that hosts the AI agent, model deployments, and connections. |
| **Azure AI Search** | Indexes your documents so the agent can search them quickly using both keywords and meaning-based (semantic) search. |
| **Azure Storage Account** | Stores your PDF files in the cloud and provides the citation links in agent responses. |
| **Azure OpenAI Models** | AI models that power the agent's language understanding (`gpt-4.1-mini`) and document search (`text-embedding-3-small`). |
| **Managed Identity** | Handles secure authentication between services — no passwords or secrets to manage. |

### Knowledge Base Pipeline

When you add documents and run the deployment, here's what happens behind the scenes:

1. **Upload** — Your PDFs are uploaded to Azure Blob Storage.
2. **Chunking** — Each document is split into page-level sections so the agent can pinpoint exact locations.
3. **Embedding** — Each section is converted into a mathematical representation (vector) that captures its meaning, enabling intelligent search.
4. **Indexing** — Sections are stored in Azure AI Search, supporting both keyword matching and meaning-based retrieval.
5. **Knowledge Base** — A knowledge base is created that allows the agent to automatically plan the best search strategy for each question.

The accelerator ships with 11 sample PDFs covering supply chain, inventory, delivery, and quality management. Replace them with your own documents for domain-specific answers.

### Azure AI Foundry Agent

| Setting | Detail |
|---|---|
| **Agent name** | `ChatAgent` |
| **Model** | `gpt-4.1-mini` (configurable via `AZURE_CHAT_MODEL`) |
| **Tool** | Knowledge Base connected via [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) |
| **Capabilities** | Document Q&A · semantic search · page-level citations · chart generation |

The agent uses **automatic query planning** — it breaks down your questions into optimal search queries, retrieves the most relevant document sections, and synthesizes an answer with direct source citations.

For deployment internals, scripts, configuration variables, and troubleshooting, see the [Deployment Guide — Foundry Deep-Dive](./DeploymentGuideFoundry.md).

---

## Documentation

| Document | Description |
|---|---|
| [Foundry IQ Overview](./README.md) | This file — what Foundry IQ does, getting started, and architecture overview. |
| [Deployment Guide — Foundry Deep-Dive](./DeploymentGuideFoundry.md) | Technical deployment details, scripts, configuration, and troubleshooting. |
| [Sample Questions](./sample_questions.md) | Example queries for the Azure AI Foundry Agent organized by category. |
| [Top-level Deployment Guide](../DeploymentGuide.md) | Full `azd up` walkthrough for the complete solution. |
