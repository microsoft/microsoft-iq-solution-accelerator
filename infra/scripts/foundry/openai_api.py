"""
Azure OpenAI client factory for the Microsoft IQ Solution Accelerator.
"""

import logging

from azure.identity import DefaultAzureCredential

# Module-level logger — inherits configuration from the root logger set up
# by setup_logging() in the entry-point scripts.  No handlers or levels are
# configured here.
logger = logging.getLogger(__name__)


def create_openai_client(ai_endpoint: str):
    """Create an Azure OpenAI client authenticated via DefaultAzureCredential.

    Args:
        ai_endpoint: Azure AI Services / OpenAI endpoint URL.

    Returns:
        Authenticated ``AzureOpenAI`` client instance.
    """
    from openai import AzureOpenAI

    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    return AzureOpenAI(
        azure_endpoint=ai_endpoint,
        api_key=token.token,
        api_version="2024-10-21",
    )
