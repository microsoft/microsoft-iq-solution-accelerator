# Deployment Guide — Foundry IQ Deep-Dive

This is a **Foundry-focused companion** to the top-level [DeploymentGuide.md](../DeploymentGuide.md). It covers everything specific to the **Foundry IQ** half of the accelerator — the Azure AI infrastructure, Knowledge Base pipeline, Azure AI Foundry Agent setup, deployment scripts, and known limitations.

> **Looking for the standard `azd up` walkthrough?** Use [`docs/DeploymentGuide.md`](../DeploymentGuide.md). It covers prerequisites, environment setup options, `azd up` commands, optional configuration variables, and cleanup. This guide is for users who want to understand or extend the Foundry-specific behavior.

There are two deployment paths:

| Path | Provisions | When to use |
|---|---|---|
| **Full automated deployment** ([DeploymentGuide.md](../DeploymentGuide.md)) | Azure infrastructure (Bicep) + Fabric workspace + Foundry resources | Default; the supported end-to-end path. |
| **This guide** | Same as full deployment | When you need Foundry internals, troubleshooting, or want to extend the knowledge base or agent configuration. |

---

## Table of Contents

1. [Foundry-Specific Prerequisites](#foundry-specific-prerequisites)
2. [Infrastructure Provisioned](#infrastructure-provisioned)
3. [Phase 2 — Foundry Bootstrap Details](#phase-2--foundry-bootstrap-details)
4. [Helper Modules](#helper-modules)
5. [Knowledge Base Pipeline](#knowledge-base-pipeline)
6. [Azure AI Foundry Agent Configuration](#azure-ai-foundry-agent-configuration)
7. [Idempotency](#idempotency)
8. [Configuration Variables](#configuration-variables)
9. [Verification](#verification)
10. [Known Limitations](#known-limitations)
11. [Additional Resources](#additional-resources)

---

## Foundry-Specific Prerequisites

In addition to the [common requirements](../DeploymentGuide.md#deployment-environment-setup) listed in the main guide, the Foundry portion requires:

### Azure resources

- **Azure subscription** with permissions to create AI services, storage accounts, and search services.
- **Azure OpenAI access** — the subscription must be approved for Azure OpenAI Service.
- **`Microsoft.CognitiveServices`** and **`Microsoft.Search`** resource providers registered on the subscription.

### Model availability

- **`gpt-4.1-mini`** (or your `AZURE_CHAT_MODEL` override) available in the target `AZURE_AI_DEPLOYMENTS_LOCATION` region.
- **`text-embedding-3-small`** (or your `AZURE_OPENAI_EMBEDDING_MODEL` override) available in the same region.

> Check model availability at [Azure OpenAI model summary](https://learn.microsoft.com/azure/ai-services/openai/concepts/models#model-summary-table-and-region-availability).

---

## Infrastructure Provisioned

Phase 1 (Bicep) creates the following Foundry-related resources in a single resource group:

| Resource | Purpose |
|---|---|
| **[Azure AI Foundry Hub & Project](https://learn.microsoft.com/azure/ai-studio/concepts/ai-resources)** | Container for agents, model deployments, knowledge bases, and connections. |
| **[Azure AI Search](https://learn.microsoft.com/azure/search/search-what-is-azure-search)** | Document indexing with vector + keyword hybrid search. |
| **[Azure Storage Account](https://learn.microsoft.com/azure/storage/common/storage-account-overview)** | Blob storage for PDF documents with direct citation links. |
| **Azure OpenAI deployments** | `gpt-4.1-mini` for chat (150K TPM) and `text-embedding-3-small` for embeddings (80K TPM). |
| **User-assigned Managed Identity** | Secure authentication between Foundry, Search, and Storage — no secrets stored. |
| **Log Analytics + Application Insights** | Diagnostics and monitoring for the Foundry project and AI Search. |
| **Foundry connections** | Project connections wiring Foundry to AI Search, Blob Storage, and the Knowledge Base MCP endpoint. |

---

## Phase 2 — Foundry Bootstrap Details

[`install_microsoft_iq_solution.py`](../../infra/scripts/install_microsoft_iq_solution.py) is the `postprovision` hook that runs after Bicep. The **Foundry-side** steps (1–2) are:

| Step | Module | What it does |
|---|---|---|
| 1 · `setup_knowledge_base` | [`foundry/step_knowledge_base.py`](../../infra/scripts/foundry/step_knowledge_base.py) | Creates the Azure AI Search index, uploads PDFs from [`src/foundry/data/documents/`](../../src/foundry/data/documents/) to blob storage, generates vector embeddings, and provisions the Foundry IQ knowledge source and knowledge base. |
| 2 · `setup_agent` | [`foundry/step_agent_setup.py`](../../infra/scripts/foundry/step_agent_setup.py) | Creates the `ChatAgent` in the Foundry project, wires it to the Knowledge Base via an [MCP](https://modelcontextprotocol.io/introduction) tool connection. **Best-effort**: transient platform errors are logged as warnings and the deployment continues. |

---

## Helper Modules

The Foundry bootstrap calls into these helper modules under [`infra/scripts/foundry/`](../../infra/scripts/foundry/):

| Module | Role |
|---|---|
| [`search_api.py`](../../infra/scripts/foundry/search_api.py) | Azure AI Search client — index management, document upload, embedding generation. |
| [`blob_api.py`](../../infra/scripts/foundry/blob_api.py) | Azure Blob Storage client — PDF upload and SAS URL generation for citations. |
| [`agent_api.py`](../../infra/scripts/foundry/agent_api.py) | Foundry Agent API client — agent creation, tool attachment, knowledge base wiring. |
| [`test_agent.py`](../../infra/scripts/foundry/test_agent.py) | CLI test harness — sends a sample question to the deployed agent and prints the response. |

Cross-cutting helpers under [`infra/scripts/common/`](../../infra/scripts/common/) are shared with the Fabric deployment:

| Module | Role |
|---|---|
| [`config.py`](../../infra/scripts/common/config.py) | `SOLUTION_NAME`, naming conventions. |
| [`env_utils.py`](../../infra/scripts/common/env_utils.py) | `get_required_env_var()` and environment parsing. |
| [`logging_config.py`](../../infra/scripts/common/logging_config.py) | `setup_logging()` — set `LOG_LEVEL=DEBUG` for HTTP-level traces. |
| [`step_printer.py`](../../infra/scripts/common/step_printer.py) | `print_step()`, `print_steps_summary()` — deployment output formatting. |

---

## Knowledge Base Pipeline

The knowledge base pipeline transforms raw PDF documents into a searchable, citation-ready index:

```
PDF documents → Blob Storage upload → Page-aware chunking → Vector embeddings → AI Search index
                                                                                      ↓
                                                                           Knowledge Source → Knowledge Base → MCP Connection → Azure AI Foundry Agent
```

### Document processing

1. **Upload**: PDFs from `src/foundry/data/documents/` are uploaded to Azure Blob Storage.
2. **Chunking**: Documents are split into page-aware chunks for precise citations (page numbers preserved).
3. **Embedding**: Each chunk is vectorized using `text-embedding-3-small` for semantic search.
4. **Indexing**: Chunks are indexed in Azure AI Search with both vector embeddings and full-text content for hybrid retrieval.

### Knowledge base components

| Component | Default name | Purpose |
|---|---|---|
| **Search Index** | `{solution_suffix}-documents` | Chunked PDFs with vector embeddings. Override with `AZURE_AI_SEARCH_INDEX`. |
| **Knowledge Source** | `{solution_suffix}-ks` | Foundry IQ pointer to the AI Search index. |
| **Knowledge Base** | `{solution_suffix}-kb` | Knowledge base with automatic query planning over the source. |
| **KB MCP Connection** | `{solution_suffix}-kb-mcp-connection` | Exposes the KB to the agent via [Model Context Protocol](https://modelcontextprotocol.io/introduction). Override with `KB_MCP_CONNECTION_NAME`. |

### Sample documents included

The accelerator ships with 11 sample PDFs covering supply chain, inventory, delivery, and quality management topics:

| Document | Topic |
|---|---|
| `supplier_onboarding_approval_process.pdf` | Supplier onboarding workflow |
| `supplier_management.pdf` | Supplier relationship management |
| `supplier_performance_evaluation_framework.pdf` | Evaluation criteria and metrics |
| `supplier_terms_and_conditions.pdf` | Contractual terms |
| `supply_chain_risk_management.pdf` | Risk identification and mitigation |
| `quality_control_manual.pdf` | Quality standards and procedures |
| `inventory_management_standards.pdf` | Inventory policies |
| `inventory_logistics.pdf` | Logistics operations |
| `delivery_operations_manual.pdf` | Delivery procedures |
| `delivery_operations.pdf` | Delivery workflows |
| `environmental_safety_compliance_policy.pdf` | Environmental and safety compliance |

Replace these with your own documents and re-run `azd up` to rebuild the knowledge base.

---

## Azure AI Foundry Agent Configuration

The `ChatAgent` is configured with:

| Setting | Value |
|---|---|
| **Model** | `gpt-4.1-mini` (override with `AZURE_CHAT_MODEL` or `AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME`) |
| **Tool** | Knowledge Base MCP connection for document retrieval |
| **Capabilities** | Document Q&A, semantic search, citation generation, chart creation |

The agent uses **automatic query planning** — it decomposes user questions into optimal search queries against the knowledge base, then synthesizes answers with page-level citations and direct blob storage links.

---

## Idempotency

Both Foundry steps are safe to re-run:

- **`setup_knowledge_base`** — recreates the search index, re-uploads all PDFs, and re-provisions the knowledge source and knowledge base. Existing documents are overwritten.
- **`setup_agent`** — recreates the agent if missing or updates the existing configuration. MCP tool attachment is re-applied.

Re-running `azd up` is the recommended way to update the knowledge base after adding new documents.

---

## Configuration Variables

Foundry-specific variables set via `azd env set <KEY> <VALUE>` before `azd up`:

| Variable | Purpose | Default |
|---|---|---|
| `AZURE_AI_DEPLOYMENTS_LOCATION` | Region for AI model deployments (**required**) | _(prompted)_ |
| `AZURE_CHAT_MODEL` | Chat completion model name | `gpt-4.1-mini` |
| `AZURE_OPENAI_EMBEDDING_MODEL` | Embedding model name | `text-embedding-3-small` |
| `AZURE_AI_SEARCH_INDEX` | Search index name | `{solution_suffix}-documents` |
| `KB_MCP_CONNECTION_NAME` | MCP connection name | `{solution_suffix}-kb-mcp-connection` |
| `AZURE_EXISTING_AI_PROJECT_RESOURCE_ID` | Use an existing Foundry project | _(empty)_ |
| `LOG_LEVEL` | Script logging verbosity | `INFO` |

---

## Verification

### In the Foundry portal

Open [ai.azure.com](https://ai.azure.com) → select your hub → select your project. Confirm:

1. **Knowledge Bases** → `{solution_suffix}-kb` exists, status is *Ready*, and lists `{solution_suffix}-ks` as its source.
2. **Agents** → `ChatAgent` exists, its model matches your deployment, and the **Tools** panel shows the MCP connection attached.
3. **Connections** → AI Search, Blob Storage, and KB MCP connections are all *Connected*.

### From the CLI

```bash
# From the repository root
python infra/scripts/foundry/test_agent.py
```

This sends a sample question to the deployed agent and prints the response with citations.

> If `setup_agent` finished with a warning during deployment, this verification is the recommended way to check whether the agent was created. If `ChatAgent` is missing, re-run `azd up`.

---

## Known Limitations

### 1. Agent creation is best-effort

**Symptom**: `setup_agent` logs a warning but deployment completes successfully (exit code 0).

**Why**: The Foundry Agent API may experience transient errors during agent creation or MCP tool attachment.

**Fix**: Re-run `azd up`. The step is idempotent and will retry agent creation.

### 2. Model quota or region availability

**Symptom**: Bicep deployment fails with a quota or capacity error for OpenAI model deployments.

**Why**: The target region may not have sufficient quota for `gpt-4.1-mini` (150K TPM) or `text-embedding-3-small` (80K TPM).

**Fix**: Either request a quota increase, or deploy to a different region:
```bash
azd env set AZURE_AI_DEPLOYMENTS_LOCATION <new-region>
azd up
```

### 3. Empty knowledge base responses

**Symptom**: The agent responds with generic answers and no citations.

**Why**: No PDF documents were present in `src/foundry/data/documents/` at deployment time, or the upload/indexing step failed silently.

**Fix**: Add PDFs to the documents folder and re-run `azd up` to rebuild the index.

### 4. PDF upload size limits

**Symptom**: Large PDFs fail to upload or index.

**Why**: Azure AI Search has document size limits for indexing operations.

**Fix**: Split large PDFs into smaller files (< 16 MB each) before uploading.

---

## Additional Resources

- [Top-level Deployment Guide](../DeploymentGuide.md) — the standard `azd up` walkthrough.
- [Foundry IQ Architecture Overview](./README.md) — architecture and getting started.
- [Sample Questions](./sample_questions.md) — example queries for the Azure AI Foundry Agent.
- [Azure AI Foundry documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Azure AI Search documentation](https://learn.microsoft.com/azure/search/)
- [Azure OpenAI documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Model Context Protocol](https://modelcontextprotocol.io/introduction)
- [Solution accelerator repository](https://github.com/microsoft/microsoft-iq-solution-accelerator)
