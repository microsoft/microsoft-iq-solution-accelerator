#!/usr/bin/env python3
"""
Shared environment variable and file I/O helpers for the Microsoft IQ
deployment scripts.

These helpers are imported by the entry-point scripts and by both the
``fabric`` and ``foundry`` domain packages.
"""

import json
import logging
import os
import shutil
import subprocess
import sys
from typing import Optional

# Module-level logger — inherits configuration from the root logger set up
# by setup_logging() in the entry-point scripts.  No handlers or levels are
# configured here; this follows the Python convention that library modules
# only acquire loggers and never configure them.
logger = logging.getLogger(__name__)


def read_file_content(file_path: str) -> str:
    """
    Read content from a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        Exception: If file can't be read
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")


def get_required_env_var(var_name: str) -> str:
    """
    Get required environment variable or exit with error.
    
    Args:
        var_name: Name of the environment variable
        
    Returns:
        Value of the environment variable
        
    Raises:
        SystemExit: If environment variable is not set
    """
    value = os.getenv(var_name)
    if not value:
        logger.error(f"Required environment variable '{var_name}' is not set")
        logger.error("   Please ensure the variable is set before running this script.")
        sys.exit(1)
    return value


def parse_workspace_administrators(
    capacity_administrators_json: Optional[str],
    fabric_workspace_admins: Optional[str],
) -> Optional[list]:
    """
    Combine administrator identities from environment variable values.

    Args:
        capacity_administrators_json: JSON-array string from
            ``AZURE_FABRIC_CAPACITY_ADMINISTRATORS``.
        fabric_workspace_admins: Comma-separated string from
            ``FABRIC_WORKSPACE_ADMINISTRATORS``.

    Returns:
        List of administrator identity strings, or ``None`` if the list is empty.
    """
    administrators: list = []

    if capacity_administrators_json:
        try:
            administrators.extend(json.loads(capacity_administrators_json))
        except json.JSONDecodeError:
            logger.warning("AZURE_FABRIC_CAPACITY_ADMINISTRATORS is not valid JSON – ignoring")

    if fabric_workspace_admins:
        administrators.extend(
            admin.strip()
            for admin in fabric_workspace_admins.split(",")
            if admin.strip()
        )

    return administrators if administrators else None


def set_azd_env_var(name: str, value: str) -> bool:
    """Persist a key/value into the active azd environment.

    Best-effort wrapper around ``azd env set``. Returns ``False`` (and
    logs) if the ``azd`` CLI is unavailable or the command fails (e.g.
    no active azd environment). Empty values are skipped.
    """
    if not value:
        return False

    if shutil.which("azd") is None:
        logger.debug(f"Skipping azd env set for '{name}' – 'azd' CLI not found")
        return False

    try:
        subprocess.run(
            ["azd", "env", "set", name, value],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        logger.warning(
            f"Could not persist '{name}' to azd environment: {stderr or exc}"
        )
        return False
    except OSError as exc:
        logger.warning(f"Could not invoke 'azd env set' for '{name}': {exc}")
        return False

