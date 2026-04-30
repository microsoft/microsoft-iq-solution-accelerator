"""
Shared configuration constants for Foundry deployment scripts.
"""

import os

SOLUTION_NAME = "Microsoft IQ"

# Paths derived from the repository layout.
# config.py lives at <repo-root>/infra/scripts/foundry/helpers/config.py
# so we walk up 4 levels to reach <repo-root>.
_HELPERS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HELPERS_DIR))))

DATA_DIR = os.path.join(REPO_ROOT, "src", "foundry", "data")
