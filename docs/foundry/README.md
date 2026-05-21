# Foundry IQ Architecture

## Overview

The Foundry component of the Microsoft IQ Solution Accelerator implements a document-based question answering system using Azure AI Foundry. It combines a Knowledge Base pipeline with an intelligent Azure AI Foundry Agent to deliver grounded answers with source citations from your PDF documents.

## Foundry IQ Architecture

The key components of the Foundry IQ architecture are as follows:

- Azure AI Foundry Hub & Project for agent management and model deployments
- Azure AI Search for document indexing with hybrid (vector + keyword) retrieval
- Azure Blob Storage for PDF document storage with direct citation links
- Knowledge Base pipeline with page-aware chunking and semantic search
- Azure AI Foundry Agent with MCP-based tool access to the Knowledge Base

## Key Components

### Infrastructure

The deployment provisions these Azure resources automatically via `azd up`:

| Resource | Purpose |
|---|---|
| **Azure AI Foundry Hub & Project** | Core AI platform — agents, model deployments, knowledge bases, and connections. |
| **Azure AI Search** | Document indexing with vector embeddings and keyword search for hybrid retrieval. |
| **Azure Storage Account** | Blob storage for PDF documents; provides direct citation links in agent responses. |
| **Azure OpenAI Models** | `gpt-4.1-mini` for chat completion (150K TPM) and `text-embedding-3-small` for embeddings (80K TPM). |
| **Managed Identity** | Secure service-to-service authentication — no secrets stored. |

### Knowledge Base

The Knowledge Base pipeline transforms raw PDFs into a searchable, citation-ready index:

1. **Upload** — PDFs from [`src/foundry/data/documents/`](../../src/foundry/data/documents/) are stored in Azure Blob Storage.
2. **Chunking** — Documents are split into page-aware chunks, preserving page numbers for precise citations.
3. **Embedding** — Each chunk is vectorized using `text-embedding-3-small` for semantic search.
4. **Indexing** — Chunks are indexed in Azure AI Search with both vector and full-text content for hybrid retrieval.
5. **Knowledge Source & Base** — A Foundry IQ knowledge source points to the search index; a knowledge base enables automatic query planning over it.

The accelerator ships with 11 sample PDFs covering supply chain, inventory, delivery, and quality management. Replace them with your own documents for domain-specific answers.

### Azure AI Foundry Agent

| Setting | Detail |
|---|---|
| **Agent name** | `ChatAgent` |
| **Model** | `gpt-4.1-mini` (configurable via `AZURE_CHAT_MODEL`) |
| **Tool** | Knowledge Base via [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) connection |
| **Capabilities** | Document Q&A · semantic search · page-level citations with blob links · chart generation |

The agent uses **automatic query planning** — it decomposes user questions into optimal search queries, then synthesizes answers grounded in your documents with direct source citations.

Additional information on the deployment pipeline and scripts can be found in [Deployment Guide — Foundry deep-dive](./DeploymentGuideFoundry.md).

## Getting Started

1. **Deploy**: Run `azd up` to provision all infrastructure and create the agent.
2. **Add documents**: Place your PDF files in [`src/foundry/data/documents/`](../../src/foundry/data/documents/) and re-run `azd up` to rebuild the knowledge base.
3. **Access the agent**: Open [Azure AI Foundry](https://ai.azure.com) → select your hub → select your project → **Agents** → `ChatAgent`.
4. **Start chatting**: Begin with discovery questions like *"What documents are available?"* to explore your knowledge base.

> For the full deployment walkthrough, see the [top-level Deployment Guide](../DeploymentGuide.md). For Foundry-specific internals, troubleshooting, and configuration, see the [Foundry Deployment Deep-Dive](./DeploymentGuideFoundry.md).

## Document Management

| Action | How |
|---|---|
| **Add documents** | Place PDF files in [`src/foundry/data/documents/`](../../src/foundry/data/documents/) |
| **Update the knowledge base** | Re-run `azd up` — this re-uploads PDFs and rebuilds the search index |
| **Verify indexing** | Check [ai.azure.com](https://ai.azure.com) → Knowledge Bases → `{solution_suffix}-kb` → status *Ready* |
| **Test the agent** | Run `python infra/scripts/foundry/test_agent.py` from the repository root |

### Citation behavior

Each agent response includes:
- **Page numbers** referencing the exact source page in the original PDF
- **Direct blob links** to the source documents in Azure Storage
- **Source attribution** showing which document(s) were used

## Tips for Best Results

- **Be specific** — ask about policies, procedures, or specific document content rather than broad topics.
- **Use context** — reference document types or names you've uploaded for more precise retrieval.
- **Request citations** — the agent provides direct links to source pages; ask for them explicitly if needed.
- **Ask follow-ups** — build on previous answers for deeper analysis.
- **Start with discovery** — begin with *"What documents are available?"* to understand your knowledge base scope.

## Sample Questions

For a comprehensive list of example queries organized by category, see **[Sample Questions](./sample_questions.md)**.

Quick examples:
- *"What are the qualification criteria for new suppliers?"*
- *"Summarize the key steps in the supplier onboarding process"*
- *"What performance metrics are used for supplier monitoring?"*

---

## Documentation

| Document | Description |
|---|---|
| [Foundry IQ Architecture](./README.md) | This file — architecture overview and getting started. |
| [Deployment Guide — Foundry Deep-Dive](./DeploymentGuideFoundry.md) | Foundry-specific deployment details, scripts, configuration, and troubleshooting. |
| [Sample Questions](./sample_questions.md) | Example queries for the Azure AI Foundry Agent organized by category. |
| [Top-level Deployment Guide](../DeploymentGuide.md) | Full `azd up` walkthrough for the complete solution. |
