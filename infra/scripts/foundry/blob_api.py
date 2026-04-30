"""
Azure Blob Storage client and upload operations for the Microsoft IQ Solution Accelerator.
"""

import logging
from pathlib import Path

from azure.identity import DefaultAzureCredential

# Module-level logger — inherits configuration from the root logger set up
# by setup_logging() in the entry-point scripts.  No handlers or levels are
# configured here.
logger = logging.getLogger(__name__)


def create_blob_service_client(blob_endpoint: str):
    """Create an Azure Blob Storage service client.

    Args:
        blob_endpoint: Azure Blob Storage service endpoint URL.

    Returns:
        Authenticated ``BlobServiceClient`` instance.
    """
    from azure.storage.blob import BlobServiceClient

    return BlobServiceClient(blob_endpoint, DefaultAzureCredential())


def upload_pdf_to_blob(
    blob_service_client,
    blob_endpoint: str,
    container_name: str,
    pdf_path,
) -> str:
    """Upload a PDF file to Azure Blob Storage and return its URL.

    Creates the container if it does not already exist.

    Args:
        blob_service_client: Authenticated ``BlobServiceClient``.
        blob_endpoint: Storage service endpoint URL (used to build the returned URL).
        container_name: Target blob container name.
        pdf_path: Path to the PDF file (``str`` or ``Path``).

    Returns:
        Blob URL string for the uploaded file.
    """
    pdf_path = Path(pdf_path)
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
        logger.debug(f"      Created blob container '{container_name}'")
    except Exception:
        pass  # container already exists

    with open(pdf_path, "rb") as data:
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=pdf_path.name,
        )
        blob_client.upload_blob(data, overwrite=True)

    blob_url = f"{blob_endpoint.rstrip('/')}/{container_name}/{pdf_path.name}"
    logger.debug(f"      Uploaded '{pdf_path.name}' to blob storage")
    return blob_url
