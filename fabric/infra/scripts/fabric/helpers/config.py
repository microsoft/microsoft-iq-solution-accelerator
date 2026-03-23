"""
Shared configuration constants for Fabric deployment scripts.
"""

import os

SOLUTION_NAME = "Microsoft IQ"

# Paths derived from the repository layout.
# config.py lives at <repo-root>/fabric/infra/scripts/fabric/helpers/config.py
# so we walk up 5 levels to reach <repo-root>.
_HELPERS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HELPERS_DIR)))))


def default_workspace_name(suffix: str) -> str:
    """Return the default workspace name for a given solution suffix."""
    return f"{SOLUTION_NAME} - {suffix}"
