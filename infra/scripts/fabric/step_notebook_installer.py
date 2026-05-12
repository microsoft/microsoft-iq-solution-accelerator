#!/usr/bin/env python3
"""
Installer notebook upload, patching, and execution helpers.
"""

import base64
import json
import logging
import os
import subprocess

from common.config import REPO_ROOT
from common.env_utils import read_file_content
from fabric.fabric_api import FabricApiError

# Module-level logger — inherits configuration from the root logger set up
# by setup_logging() in the entry-point scripts.  No handlers or levels are
# configured here; this follows the Python convention that library modules
# only acquire loggers and never configure them.
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INSTALLER_NOTEBOOK_NAME = "fabric_solution_installer"


# ---------------------------------------------------------------------------
# Notebook helpers
# ---------------------------------------------------------------------------


def get_notebook_path() -> str:
    """Return the absolute path to the installer notebook file.

    The notebook lives at ``<repo-root>/infra/fabric/deploy/fabric_solution_installer.ipynb``.
    """
    return os.path.join(REPO_ROOT, "infra", "fabric", "deploy", f"{INSTALLER_NOTEBOOK_NAME}.ipynb")


def encode_notebook(notebook_path: str) -> str:
    """
    Read a ``.ipynb`` file and return its content as a Base64 string.

    Args:
        notebook_path: Absolute path to the notebook file.

    Returns:
        Base64-encoded notebook content (UTF-8).

    Raises:
        FileNotFoundError: If the notebook file does not exist.
        ValueError: If the file is not valid JSON.
    """
    content = read_file_content(notebook_path)  # raises FileNotFoundError if missing
    notebook_json = json.loads(content)         # validate JSON before encoding
    raw_bytes = json.dumps(notebook_json).encode("utf-8")
    return base64.b64encode(raw_bytes).decode("utf-8")


def _get_current_git_branch() -> str | None:
    """Get the name of the currently checked out git branch.

    Returns:
        str: The branch name, or None if not in a git repository or if detection fails.
    """
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        branch = result.stdout.strip()
        return branch if branch else None
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        logger.debug(f"Could not detect git branch: {exc}")
        return None


def _patch_notebook_for_github_branch(notebook_json: dict, branch_name: str) -> dict:
    """Update the ``GITHUB_BRANCH`` value in the installer notebook.

    Modifies the notebook *in-place* to replace the GITHUB_BRANCH variable
    assignment with the current branch name.

    Args:
        notebook_json: Parsed notebook dict (ipynb JSON).
        branch_name: The branch name to set.

    Returns:
        The mutated *notebook_json* dict.
    """
    for cell in notebook_json.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source_lines = cell.get("source", [])
        source_text = "".join(source_lines)

        # Update GITHUB_BRANCH value if found
        if "GITHUB_BRANCH" in source_text and "=" in source_text:
            new_lines = []
            for line in source_lines:
                if line.lstrip().startswith("GITHUB_BRANCH") and "=" in line:
                    # Preserve indentation and spacing style
                    indent = line[: len(line) - len(line.lstrip())]
                    # Extract spacing pattern (spaces around =)
                    before_eq = line.split("=")[0]
                    spaces_before = len(before_eq) - len(before_eq.rstrip())
                    new_lines.append(f'{indent}GITHUB_BRANCH{" " * spaces_before}= "{branch_name}"\n')
                else:
                    new_lines.append(line)
            cell["source"] = new_lines

    return notebook_json


def _patch_notebook_for_github_token(notebook_json: dict, github_token: str) -> dict:
    """Inject ``GITHUB_TOKEN`` into the installer notebook.

    Modifies the notebook *in-place* so that:
    * A ``GITHUB_TOKEN = "<value>"`` variable assignment is added after the
      ``GITHUB_BRANCH`` assignment in the configuration cell.
    * ``github_token=GITHUB_TOKEN`` is added to the ``launcher.download_and_deploy``
      call.

    Args:
        notebook_json: Parsed notebook dict (ipynb JSON).
        github_token: The token value to inject.

    Returns:
        The mutated *notebook_json* dict.
    """
    for cell in notebook_json.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source_lines = cell.get("source", [])
        source_text = "".join(source_lines)

        # -- Inject GITHUB_TOKEN variable after GITHUB_BRANCH line --
        if "GITHUB_BRANCH" in source_text and "GITHUB_TOKEN" not in source_text:
            new_lines = []
            for line in source_lines:
                new_lines.append(line)
                if line.lstrip().startswith("GITHUB_BRANCH"):
                    # Preserve the same indentation
                    indent = line[: len(line) - len(line.lstrip())]
                    new_lines.append(f'{indent}GITHUB_TOKEN     = "{github_token}"\n')
            cell["source"] = new_lines

        # -- Add github_token=GITHUB_TOKEN to download_and_deploy call --
        source_text = "".join(cell.get("source", []))
        if "download_and_deploy" in source_text and "github_token" not in source_text:
            new_lines = []
            for line in cell["source"]:
                new_lines.append(line)
                if "branch" in line and "GITHUB_BRANCH" in line:
                    indent = line[: len(line) - len(line.lstrip())]
                    new_lines.append(f"{indent}github_token=GITHUB_TOKEN,\n")
            cell["source"] = new_lines

    return notebook_json


def upload_installer_notebook(workspace_client, notebook_path: str, github_token: str | None = None) -> str:
    """Upload (or update) the installer notebook in the workspace.

    If a notebook with the same name already exists it will be updated in-place;
    otherwise a new notebook is created.

    The notebook is patched in-memory before upload to:
    * Update GITHUB_BRANCH to the currently checked out branch
    * Inject GITHUB_TOKEN if provided

    Args:
        workspace_client: Authenticated :class:`FabricWorkspaceApiClient`.
        notebook_path: Absolute path to the local ``.ipynb`` file.
        github_token: Optional GitHub token to inject into the notebook.

    Returns:
        str: The notebook ID of the uploaded/updated notebook.

    Raises:
        FileNotFoundError: If the notebook file does not exist.
        FabricApiError: If the Fabric API call fails.
    """
    logger.info(f"   Reading notebook file: {notebook_path}")

    # Always read and parse the notebook for patching
    content = read_file_content(notebook_path)
    notebook_json = json.loads(content)
    patched = False

    # Detect and patch current git branch
    current_branch = _get_current_git_branch()
    if current_branch:
        logger.info(f"   Patching notebook with GITHUB_BRANCH = '{current_branch}'")
        _patch_notebook_for_github_branch(notebook_json, current_branch)
        patched = True
    else:
        logger.info("   Could not detect git branch, using notebook default")

    # Patch GitHub token if provided
    if github_token:
        logger.info("   Patching notebook with GITHUB_TOKEN")
        _patch_notebook_for_github_token(notebook_json, github_token)
        patched = True

    # Encode the notebook (patched or original)
    if patched:
        raw_bytes = json.dumps(notebook_json).encode("utf-8")
        notebook_base64 = base64.b64encode(raw_bytes).decode("utf-8")
    else:
        notebook_base64 = encode_notebook(notebook_path)

    logger.info(f"   Checking for existing notebook: {INSTALLER_NOTEBOOK_NAME}")
    existing = workspace_client.get_notebook_by_name(INSTALLER_NOTEBOOK_NAME)

    if existing:
        notebook_id = existing["id"]
        logger.info(f"   Notebook already exists ({notebook_id}) \u2013 updating definition")
        workspace_client.update_notebook(notebook_id, notebook_base64)
        logger.info(f"   Notebook updated: {INSTALLER_NOTEBOOK_NAME}")
    else:
        logger.info(f"   Creating notebook: {INSTALLER_NOTEBOOK_NAME}")
        workspace_client.create_notebook(INSTALLER_NOTEBOOK_NAME, notebook_base64)
        refreshed = workspace_client.get_notebook_by_name(INSTALLER_NOTEBOOK_NAME)
        if not refreshed:
            raise FabricApiError(
                f"Notebook '{INSTALLER_NOTEBOOK_NAME}' was not found after creation"
            )
        notebook_id = refreshed["id"]
        logger.info(f"   Notebook created: {INSTALLER_NOTEBOOK_NAME} ({notebook_id})")

    return notebook_id


def _get_monitoring_url(workspace_client, notebook_id: str, job_instance_id: str) -> str | None:
    """Return the Fabric monitoring URL for a failed notebook job.

    Looks up the Livy session matching *job_instance_id* and builds the
    monitoring URL from its ``livyId``.

    Args:
        workspace_client: Authenticated :class:`FabricWorkspaceApiClient`.
        notebook_id: ID of the notebook whose job failed.
        job_instance_id: Job instance ID from the :meth:`schedule_notebook_job` result.

    Returns:
        str: Monitoring URL, or ``None`` if it cannot be determined.
    """
    try:
        livy_sessions = workspace_client.list_livy_sessions(notebook_id)
        matched_session = next(
            (s for s in livy_sessions if s.get("jobInstanceId") == job_instance_id), None
        )
        if not matched_session:
            logger.debug(f"   No Livy session matched job instance {job_instance_id}")
            return None

        livy_id = matched_session.get("livyId")
        if not livy_id:
            logger.debug("   Livy session has no livyId field")
            return None

        return (
            f"https://app.fabric.microsoft.com/workloads/de-ds/monitor"
            f"/{notebook_id}/{livy_id}?experience=fabric-developer"
        )
    except Exception as exc:
        logger.debug(f"   Could not retrieve monitoring URL: {exc}")
        return None


def run_installer_notebook(workspace_client, notebook_id: str, monitor_interval: int = 20) -> None:
    """Schedule and monitor the installer notebook job until completion.

    Args:
        workspace_client: Authenticated :class:`FabricWorkspaceApiClient`.
        notebook_id: ID of the notebook to execute.
        monitor_interval: Seconds between status-polling requests (default: 20).

    Raises:
        FabricApiError: If the notebook job fails to start or returns an error status.
    """
    logger.info(f"   Scheduling notebook job: {INSTALLER_NOTEBOOK_NAME} ({notebook_id})")
    result = workspace_client.schedule_notebook_job(notebook_id, monitor_interval=monitor_interval)

    status = result.get("status", "Unknown")
    duration = result.get("duration", "N/A")

    logger.info(f"   Execution result:")
    logger.info(f"      Status:   {status}")
    logger.info(f"      Duration: {duration}")

    if status != "Completed":
        error_detail = result.get("error", "No error details available")
        job_instance_id = result.get("details", {}).get("id")
        monitoring_url = _get_monitoring_url(workspace_client, notebook_id, job_instance_id) if job_instance_id else None
        if monitoring_url:
            logger.info(f"   Open the monitoring URL below to inspect the notebook output and find the error:")
            logger.info(f"   Monitoring URL: {monitoring_url}")
        raise FabricApiError(
            f"Installer notebook finished with status '{status}'. Error: {error_detail}"
            + (
                f"\n      To diagnose: open the monitoring URL, navigate to the failed cell,"
                f" and expand its output to find the error.\n      Monitoring URL: {monitoring_url}"
                if monitoring_url else ""
            )
        )

    logger.info(f"   Installer notebook completed successfully")
