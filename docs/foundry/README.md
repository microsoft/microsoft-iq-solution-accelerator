# Foundry IQ Architecture

## Overview

The Foundry component of the Microsoft IQ Solution Accelerator implements a document-based question answering system using Azure AI Foundry, featuring a Knowledge Base pipeline with intelligent search capabilities, an Azure AI Foundry Agent for natural language document querying, and source citations with direct links to original documents.

## Foundry IQ Architecture

The key components of the Foundry IQ architecture are as follows:

- Azure AI Foundry Hub & Project for agent management and model deployments
- Azure AI Search index with hybrid (vector and keyword) retrieval
- Azure Blob Storage for PDF document storage with citation links
- Knowledge Base pipeline with page-aware chunking and semantic search
- Azure AI Foundry Agent connected to the Knowledge Base via Model Context Protocol (MCP)

## Key Components

### Document Foundation

The solution implements a Knowledge Base pipeline that transforms PDF documents into a searchable, citation-ready index. Documents uploaded to [`src/foundry/data/documents/`](../../src/foundry/data/documents/) are stored in Azure Blob Storage and processed through page-aware chunking to preserve page numbers for precise citations. Each chunk is vectorized using the `text-embedding-3-small` embedding model and indexed in Azure AI Search, enabling both keyword matching and semantic retrieval.

The accelerator ships with 11 sample PDFs covering supply chain management, inventory standards, delivery operations, quality control, and supplier processes. These can be replaced with custom documents to build a domain-specific knowledge base.

### Knowledge Base, MCP Connection, and Azure AI Foundry Agent

The indexed documents are surfaced through a Foundry IQ Knowledge Source that points to the Azure AI Search index. From this Knowledge Source, a Knowledge Base is created with automatic query planning capabilities, enabling intelligent decomposition of user questions into optimal search queries.

An Azure AI Foundry Agent (`ChatAgent`) serves as the primary user interface, connected to the Knowledge Base through a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) connection. This agent enables users to interact with their documents through natural language queries, automatically retrieving relevant content and synthesizing answers with page-level citations and direct document links.

Additional information on the deployment pipeline, scripts, configuration, and troubleshooting can be found in [Deployment Guide — Foundry deep-dive](./DeploymentGuideFoundry.md)

Sample questions to try with the agent are documented in [Sample Questions](./sample_questions.md)

### Document Management

Document management is handled through the deployment workflow. New PDF documents are added to the [`src/foundry/data/documents/`](../../src/foundry/data/documents/) folder and the deployment is re-run using `azd up`, which re-uploads documents to Blob Storage, regenerates embeddings, rebuilds the search index, and updates the Knowledge Base. Each agent response includes page numbers referencing the exact source page, direct links to the original documents in Azure Storage, and source attribution showing which documents were used.
