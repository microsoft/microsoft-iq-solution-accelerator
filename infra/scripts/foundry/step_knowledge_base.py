#!/usr/bin/env python3
"""
Knowledge Base setup step for the Microsoft IQ deployment.

Extracts step 1 (``setup_knowledge_base``) of the deployment flow into a
single top-level function callable from the entry-point script.
"""

import logging
from pathlib import Path

from common.config import DATA_DIR
from common.pdf_utils import process_pdfs_to_documents
from foundry.blob_api import create_blob_service_client, upload_pdf_to_blob
from foundry.search_api import (
    create_or_update_knowledge_base,
    create_or_update_knowledge_source,
    create_or_update_search_index,
    create_search_client,
    create_search_index_client,
    upload_documents_to_search,
)

# Module-level logger — inherits configuration from the root logger set up
# by setup_logging() in the entry-point scripts.
logger = logging.getLogger(__name__)


def setup_knowledge_base(
    *,
    solution_name: str,
    search_endpoint: str,
    blob_endpoint: str,
    ai_endpoint: str,
    search_index_name: str,
    blob_container_name: str,
    knowledge_source_name: str,
    knowledge_base_name: str,
    embedding_model: str,
    chat_model: str,
) -> None:
    """Create Azure AI Search index, upload PDFs, and create the Knowledge Base.

    Args:
        solution_name: Human-readable solution name (used as KB description).
        search_endpoint: Azure AI Search service endpoint URL.
        blob_endpoint: Azure Blob Storage service endpoint URL.
        ai_endpoint: Azure AI Services / OpenAI endpoint URL (for embeddings + chat).
        search_index_name: Name of the search index to create or update.
        blob_container_name: Name of the blob container that will hold uploaded PDFs.
        knowledge_source_name: Name of the Foundry IQ knowledge source.
        knowledge_base_name: Name of the Foundry IQ knowledge base.
        embedding_model: OpenAI embedding model deployment name.
        chat_model: OpenAI chat model deployment name (for KB query planning).
    """
    # Locate PDFs
    data_path = Path(DATA_DIR)
    docs_dir = data_path / "documents" if (data_path / "documents").exists() else data_path
    pdf_files = list(docs_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"   No PDF files found in {docs_dir} — knowledge base will be empty")
    else:
        logger.info(f"   Found {len(pdf_files)} PDF file(s)")

    # Create Azure clients
    logger.info("   Initialising Azure clients…")
    _index_client = create_search_index_client(search_endpoint)
    _search_client = create_search_client(search_endpoint, search_index_name)
    _blob_client = create_blob_service_client(blob_endpoint)

    # Create / update search index
    logger.info("   Creating search index…")
    create_or_update_search_index(_index_client, search_index_name, embedding_model, ai_endpoint)

    # Upload PDFs and index document chunks
    pdf_blob_urls: dict = {}
    documents: list = []
    if pdf_files:
        logger.info(f"   Uploading {len(pdf_files)} PDF(s) to blob storage…")
        for _pdf_path in pdf_files:
            _url = upload_pdf_to_blob(_blob_client, blob_endpoint, blob_container_name, _pdf_path)
            pdf_blob_urls[_pdf_path.name] = _url

        logger.info("   Processing and indexing document chunks…")
        documents = process_pdfs_to_documents(pdf_files, pdf_blob_urls)
        if documents:
            upload_documents_to_search(_search_client, documents)

    # Create Knowledge Source
    logger.info("   Creating knowledge source…")
    try:
        create_or_update_knowledge_source(
            _index_client, knowledge_source_name, search_index_name, solution_name
        )
    except Exception as _exc:
        logger.warning(f"   Could not create knowledge source: {_exc}")

    # Create Knowledge Base
    logger.info("   Creating knowledge base…")
    try:
        create_or_update_knowledge_base(
            _index_client, knowledge_base_name, knowledge_source_name,
            solution_name, ai_endpoint, chat_model
        )
    except Exception as _exc:
        logger.warning(f"   Could not create knowledge base: {_exc}")
