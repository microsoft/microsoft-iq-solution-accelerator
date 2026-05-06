"""
Shared configuration constants for the Microsoft IQ deployment scripts.
"""

import os

SOLUTION_NAME = "Microsoft IQ"

# Paths derived from the repository layout.
# config.py lives at <repo-root>/infra/scripts/common/config.py
# so we walk up 3 levels to reach <repo-root>.
_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_PACKAGE_DIR)))

# Foundry data directory containing PDFs / config files used by setup_knowledge_base.
DATA_DIR = os.path.join(REPO_ROOT, "src", "foundry", "data")


def default_workspace_name(suffix: str) -> str:
    """Return the default Fabric workspace name for a given solution suffix."""
    return f"{SOLUTION_NAME} - {suffix}"

