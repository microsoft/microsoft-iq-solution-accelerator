"""
Environment loading utilities for Foundry deployment scripts.

Provides a unified way to load configuration from:
    1. Azure service settings from azd environment (.azure/<env>/.env)
    2. Project-specific settings from project root .env

Azure services (from azd):
    - AZURE_AI_AGENT_ENDPOINT
    - AZURE_AI_ENDPOINT
    - AZURE_AI_SEARCH_ENDPOINT
    - AZURE_STORAGE_BLOB_ENDPOINT
    - AZURE_CHAT_MODEL
    - AZURE_OPENAI_EMBEDDING_MODEL

Project settings (from .env):
    - SOLUTION_NAME
    - DATA_FOLDER (derived, not read from env)
"""

import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Module-level logger — inherits configuration from the root logger set up
# by setup_logging() in the entry-point scripts.
logger = logging.getLogger(__name__)

# Paths derived from the repository layout.
# env.py lives at <repo-root>/infra/scripts/foundry/helpers/env.py
# so we walk up 4 levels to reach <repo-root>.
_FILE_DIR = Path(__file__).parent
_PROJECT_ROOT = _FILE_DIR.parent.parent.parent.parent


def load_azd_env() -> bool:
    """Load environment variables from the active azd deployment.

    Reads from ``.azure/<defaultEnvironment>/.env``.

    Returns:
        True if the azd environment file was found and loaded.
    """
    azure_dir = _PROJECT_ROOT / ".azure"

    env_name = os.environ.get("AZURE_ENV_NAME", "")
    config_file = azure_dir / "config.json"

    if not env_name and config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
            env_name = config.get("defaultEnvironment", "")

    if not env_name:
        return False

    env_file = azure_dir / env_name / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
        logger.debug(f"Loaded azd environment from {env_file}")
        return True

    return False


def load_project_env() -> bool:
    """Load environment variables from the project root ``.env`` file.

    Returns:
        True if the project ``.env`` file was found and loaded.
    """
    env_file = _PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=False)
        logger.debug(f"Loaded project environment from {env_file}")
        return True
    return False


def load_all_env() -> tuple:
    """Load both azd and project environment variables.

    Returns:
        Tuple of (azd_loaded: bool, project_loaded: bool).
    """
    azd_loaded = load_azd_env()
    project_loaded = load_project_env()

    if not os.getenv("SOLUTION_NAME"):
        os.environ["SOLUTION_NAME"] = os.getenv("AZURE_ENV_NAME", "demo")

    return azd_loaded, project_loaded


def get_required_env(var_name: str, description: str = None) -> str:
    """Get a required environment variable or exit with an error.

    Args:
        var_name: Name of the environment variable.
        description: Optional human-readable description shown in the error.

    Returns:
        Value of the environment variable.

    Raises:
        SystemExit: If the environment variable is not set.
    """
    value = os.getenv(var_name)
    if not value:
        desc = f" ({description})" if description else ""
        logger.error(f"Required environment variable '{var_name}' is not set{desc}")
        logger.error("   Make sure azd deployment completed successfully.")
        sys.exit(1)
    return value


def get_data_folder() -> str:
    """Return the absolute path to the Foundry data directory (``src/foundry/data``)."""
    return str(_PROJECT_ROOT / "src" / "foundry" / "data")


def print_env_status() -> None:
    """Log the current environment status for debugging."""
    logger.info("Environment Status:")
    logger.info(f"  AZURE_ENV_NAME:             {os.getenv('AZURE_ENV_NAME', 'Not set')}")
    logger.info(f"  SOLUTION_NAME:              {os.getenv('SOLUTION_NAME', 'Not set')}")
    logger.info(f"  AZURE_AI_AGENT_ENDPOINT:    {os.getenv('AZURE_AI_AGENT_ENDPOINT', 'Not set')}")
    logger.info(f"  AZURE_AI_SEARCH_ENDPOINT:   {os.getenv('AZURE_AI_SEARCH_ENDPOINT', 'Not set')}")
    logger.info(f"  AZURE_STORAGE_BLOB_ENDPOINT:{os.getenv('AZURE_STORAGE_BLOB_ENDPOINT', 'Not set')}")
    logger.info(f"  DATA_FOLDER:                {get_data_folder()} (fixed path)")
