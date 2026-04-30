"""
Backward-compatibility shim — import from ``foundry.helpers.env`` instead.

All logic has been moved to the ``foundry`` package so it can be shared
by both the standalone scripts in this directory and the
``install_microsoft_iq_solution.py`` entry-point.

Original documentation:
Load environment variables from azd deployment and project .env file.

This module provides a unified way to load configuration:
1. Azure service settings from azd environment (.azure/<env>/.env)
2. Project-specific settings from project root .env (Fabric, industry, etc.)

Azure services (from azd):
    - AZURE_AI_AGENT_ENDPOINT
    - AZURE_AI_ENDPOINT  
    - AZURE_OPENAI_ENDPOINT
    - AZURE_AI_SEARCH_ENDPOINT
    - AZURE_STORAGE_BLOB_ENDPOINT
    - AZURE_CHAT_MODEL
    - AZURE_EMBEDDING_MODEL
    - etc.

Project settings (from .env):
    - FABRIC_WORKSPACE_ID
    - SOLUTION_NAME
    - INDUSTRY
    - USECASE
    - DATA_SIZE
    - DATA_FOLDER
    - FOUNDRY_AGENT_ID
    - etc.
"""

import os
import sys

# Add infra/scripts/ to the path so the foundry package can be found when this
# shim is imported directly (e.g. ``from load_env import load_all_env``) by
# standalone scripts running from within the foundry/ directory.
_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from foundry.helpers.env import (  # noqa: E402  (import after sys.path manipulation)
    get_data_folder,
    get_required_env,
    load_all_env,
    load_azd_env,
    load_project_env,
    print_env_status,
)

__all__ = [
    "get_data_folder",
    "get_required_env",
    "load_all_env",
    "load_azd_env",
    "load_project_env",
    "print_env_status",
]


if __name__ == "__main__":
    load_all_env()
    print_env_status()