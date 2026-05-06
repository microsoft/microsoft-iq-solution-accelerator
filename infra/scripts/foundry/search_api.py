"""
Azure AI Search client and index operations for the Microsoft IQ Solution Accelerator.

Provides client factory functions and operations for:
- Creating and managing an Azure AI Search index with semantic and vector-search configuration.
- Indexing document chunks in Azure AI Search.
- Creating an AI Search Knowledge Source and Knowledge Base (Foundry IQ).
"""

import logging

from azure.identity import DefaultAzureCredential

# Module-level logger — inherits configuration from the root logger set up
# by setup_logging() in the entry-point scripts.  No handlers or levels are
# configured here.
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Client factories
# ---------------------------------------------------------------------------


def create_search_index_client(search_endpoint: str):
    """Create an Azure AI Search index-management client.

    Args:
        search_endpoint: Azure AI Search service endpoint URL.

    Returns:
        Authenticated ``SearchIndexClient`` instance.
    """
    from azure.search.documents.indexes import SearchIndexClient

    return SearchIndexClient(search_endpoint, DefaultAzureCredential())


def create_search_client(search_endpoint: str, index_name: str):
    """Create an Azure AI Search document client for a specific index.

    Args:
        search_endpoint: Azure AI Search service endpoint URL.
        index_name: Name of the target search index.

    Returns:
        Authenticated ``SearchClient`` instance.
    """
    from azure.search.documents import SearchClient

    return SearchClient(search_endpoint, index_name, DefaultAzureCredential())


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------


def create_or_update_search_index(
    index_client,
    index_name: str,
    embedding_model: str,
    ai_endpoint: str,
) -> None:
    """Create or update an Azure AI Search index with semantic and vector-search config.

    The index schema matches the document shape produced by
    :func:`~common.pdf_utils.process_pdfs_to_documents`.
    The configured vectorizer enables query-time embedding generation
    using the specified Azure OpenAI model.

    Args:
        index_client: Authenticated ``SearchIndexClient``.
        index_name: Name of the index to create or update.
        embedding_model: OpenAI embedding model deployment name.
        ai_endpoint: Azure AI Services / OpenAI endpoint URL.
    """
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizer,
        AzureOpenAIVectorizerParameters,
        HnswAlgorithmConfiguration,
        SearchField,
        SearchFieldDataType,
        SearchIndex,
        SemanticConfiguration,
        SemanticField,
        SemanticPrioritizedFields,
        SemanticSearch,
        VectorSearch,
        VectorSearchProfile,
    )

    _EMBEDDING_DIMENSIONS = {
        "text-embedding-ada-002": 1536,
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
    }
    _ = _EMBEDDING_DIMENSIONS.get(embedding_model, 1536)  # reserved for future vector field

    fields = [
        SearchField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
        SearchField(name="title", type=SearchFieldDataType.String, searchable=True, filterable=True),
        SearchField(name="source", type=SearchFieldDataType.String, filterable=True),
        SearchField(name="page_number", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
        SearchField(name="chunk_id", type=SearchFieldDataType.Int32, sortable=True),
        SearchField(name="blob_url", type=SearchFieldDataType.String, filterable=True),
        SearchField(name="page_url", type=SearchFieldDataType.String, filterable=True),
        SearchField(name="file_size", type=SearchFieldDataType.Int32, filterable=True),
        SearchField(name="last_modified", type=SearchFieldDataType.DateTimeOffset, filterable=True),
    ]

    vectorizer = AzureOpenAIVectorizer(
        vectorizer_name="openai-vectorizer",
        parameters=AzureOpenAIVectorizerParameters(
            resource_url=ai_endpoint,
            deployment_name=embedding_model,
            model_name=embedding_model,
        ),
    )

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="default-algorithm")],
        profiles=[VectorSearchProfile(
            name="default-profile",
            algorithm_configuration_name="default-algorithm",
            vectorizer_name="openai-vectorizer",
        )],
        vectorizers=[vectorizer],
    )

    semantic_config = SemanticConfiguration(
        name="default-semantic",
        prioritized_fields=SemanticPrioritizedFields(
            content_fields=[SemanticField(field_name="content")],
            title_field=SemanticField(field_name="title"),
            keywords_fields=[SemanticField(field_name="source")],
        ),
    )

    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=SemanticSearch(configurations=[semantic_config]),
    )
    index_client.create_or_update_index(index)
    logger.info(f"   Index '{index_name}' ready")


# ---------------------------------------------------------------------------
# Document indexing
# ---------------------------------------------------------------------------


def upload_documents_to_search(search_client, documents: list) -> int:
    """Upload document chunks to an Azure AI Search index.

    Args:
        search_client: Authenticated ``SearchClient`` for the target index.
        documents: List of document dicts to upload.

    Returns:
        Number of documents successfully indexed.
    """
    result = search_client.upload_documents(documents)
    succeeded = sum(1 for r in result if r.succeeded)
    logger.info(f"   Indexed {succeeded}/{len(documents)} document chunks")
    return succeeded


# ---------------------------------------------------------------------------
# Knowledge Source and Knowledge Base (Foundry IQ)
# ---------------------------------------------------------------------------


def create_or_update_knowledge_source(
    index_client,
    ks_name: str,
    index_name: str,
    solution_name: str,
) -> None:
    """Create or update an AI Search Knowledge Source (Foundry IQ).

    Args:
        index_client: Authenticated ``SearchIndexClient``.
        ks_name: Knowledge source resource name.
        index_name: Name of the backing search index.
        solution_name: Human-readable solution name for descriptions.
    """
    from azure.search.documents.indexes.models import (
        SearchIndexFieldReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )

    knowledge_source = SearchIndexKnowledgeSource(
        name=ks_name,
        description=f"Knowledge source for {solution_name} document search index with blob storage citations.",
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=index_name,
            semantic_configuration_name="default-semantic",
            source_data_fields=[
                SearchIndexFieldReference(name="title"),
                SearchIndexFieldReference(name="source"),
                SearchIndexFieldReference(name="page_number"),
                SearchIndexFieldReference(name="blob_url"),
                SearchIndexFieldReference(name="page_url"),
            ],
            search_fields=[
                SearchIndexFieldReference(name="content"),
            ],
        ),
    )
    index_client.create_or_update_knowledge_source(knowledge_source)
    logger.info(f"   Knowledge source '{ks_name}' ready")


def create_or_update_knowledge_base(
    index_client,
    kb_name: str,
    ks_name: str,
    solution_name: str,
    ai_endpoint: str,
    chat_model: str,
) -> None:
    """Create or update an AI Search Knowledge Base (Foundry IQ).

    Args:
        index_client: Authenticated ``SearchIndexClient``.
        kb_name: Knowledge base resource name.
        ks_name: Name of the backing knowledge source.
        solution_name: Human-readable solution name for descriptions.
        ai_endpoint: Azure AI Services / OpenAI endpoint URL.
        chat_model: Chat model deployment name used for answer synthesis.
    """
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizerParameters,
        KnowledgeBase,
        KnowledgeBaseAzureOpenAIModel,
        KnowledgeRetrievalLowReasoningEffort,
        KnowledgeRetrievalOutputMode,
        KnowledgeSourceReference,
    )

    aoai_params = AzureOpenAIVectorizerParameters(
        resource_url=ai_endpoint,
        deployment_name=chat_model,
        model_name=chat_model,
    )

    knowledge_base = KnowledgeBase(
        name=kb_name,
        description=(
            f"Knowledge base for {solution_name} document retrieval "
            "with agentic query planning and blob storage citations."
        ),
        retrieval_instructions=(
            "Use this knowledge source for questions about policies, guidelines, "
            "thresholds, rules, and reference documents. Documents are stored in "
            "Azure Blob Storage with direct URLs available in the blob_url field."
        ),
        answer_instructions=(
            "Provide a concise and informative answer based on the retrieved documents. "
            "For citations, ALWAYS use the blob_url field to link directly to the source "
            "document in Azure Blob Storage, NOT the MCP endpoint. "
            "Format citations as: [Document Title](blob_url) - Page X. "
            "Include page_number when available for precise citations."
        ),
        output_mode=KnowledgeRetrievalOutputMode.ANSWER_SYNTHESIS,
        knowledge_sources=[KnowledgeSourceReference(name=ks_name)],
        models=[KnowledgeBaseAzureOpenAIModel(azure_open_ai_parameters=aoai_params)],
        retrieval_reasoning_effort=KnowledgeRetrievalLowReasoningEffort,  # type: ignore[arg-type]
    )
    index_client.create_or_update_knowledge_base(knowledge_base)
    logger.info(f"   Knowledge base '{kb_name}' ready")
