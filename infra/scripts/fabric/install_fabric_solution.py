#!/usr/bin/env python3
"""
Microsoft IQ Solution Installer

This script provides a simplified deployment entry-point for the Microsoft IQ
solution. It performs only the minimum steps needed to bootstrap the solution:

    1. setup_workspace        - Create and configure the Fabric workspace/capacity
    2. setup_administrators   - Add workspace administrators
    3. upload_installer       - Upload the installer notebook to the workspace
    4. run_installer          - Execute the installer notebook end-to-end

The installer notebook (fabric_solution_installer.ipynb) handles the remaining
solution-specific steps (lakehouse creation, data ingestion, notebook deployment,
post-deployment tasks, …) once it has been uploaded and started.

Usage:
    python install_fabric_solution.py

Environment Variables:
    The following variables are automatically set by 'azd' from main.bicep outputs and
    must be present in the environment before running this script:

    AZURE_FABRIC_CAPACITY_NAME           (required) Name of the Fabric capacity resource.
                                                    Sourced from main.bicep output:
                                                    AZURE_FABRIC_CAPACITY_NAME.
    SOLUTION_SUFFIX                      (required) Suffix used for resource naming.
                                                    Sourced from main.bicep output:
                                                    SOLUTION_SUFFIX.
    AZURE_FABRIC_CAPACITY_ADMINISTRATORS (required) JSON array of capacity administrator
                                                    identities. Sourced from main.bicep
                                                    output: AZURE_FABRIC_CAPACITY_ADMINISTRATORS.

    The following variables are optional and must be set manually if needed:

    FABRIC_WORKSPACE_NAME                (optional) Override the default workspace name
                                                    (defaults to "<SOLUTION_NAME> - <SOLUTION_SUFFIX>").
    FABRIC_WORKSPACE_ADMINISTRATORS      (optional) Comma-separated list of additional
                                                    workspace administrator identities.
    GITHUB_TOKEN                         (optional) GitHub personal access token. When set,
                                                    the installer notebook is patched to
                                                    include the token for private repo access.
"""

import base64
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime

# Add current directory to path so local modules can be imported
sys.path.append(os.path.dirname(__file__))

from helpers.logging_config import setup_logging

# Configure logging before any other imports so that library modules
# (fabric_api, graph_api, helpers.*) inherit the root logger's settings.
# The log level can be set via ``azd env set LOG_LEVEL DEBUG``.
setup_logging()

# Module-level logger for this entry-point script.  All log calls below
# use this logger; the level and handler are inherited from setup_logging().
logger = logging.getLogger(__name__)

from fabric_api import FabricApiError, create_fabric_client, create_workspace_fabric_client
from graph_api import create_graph_client
from helpers.config import REPO_ROOT, SOLUTION_NAME, default_workspace_name
from helpers.utils import (
    encode_notebook,
    get_required_env_var,
    parse_workspace_administrators,
    print_step,
    print_steps_summary,
    read_file_content,
)
from helpers.workspace import setup_workspace
from helpers.workspace_admins import setup_workspace_administrators


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INSTALLER_NOTEBOOK_NAME = "fabric_solution_installer"

ALL_DEPLOYMENT_STEPS = [
    "setup_workspace",
    "setup_administrators",
    "upload_installer",
    "run_installer",
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _notebook_path() -> str:
    """Return the absolute path to the installer notebook file.

    The notebook lives at ``<repo-root>/infra/fabric/deploy/fabric_solution_installer.ipynb``.
    """
    return os.path.join(REPO_ROOT, "infra", "fabric", "deploy", f"{INSTALLER_NOTEBOOK_NAME}.ipynb")


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


def _upload_installer_notebook(workspace_client, notebook_path: str, github_token: str | None = None) -> str:
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
        logger.info(f"   Notebook already exists ({notebook_id}) – updating definition")
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


def _run_installer_notebook(workspace_client, notebook_id: str, monitor_interval: int = 20) -> None:
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
        raise FabricApiError(
            f"Installer notebook finished with status '{status}'. Error: {error_detail}"
        )

    logger.info(f"   Installer notebook completed successfully")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Orchestrate the minimal three-step solution installation."""

    # ------------------------------------------------------------------
    # Configuration from environment variables
    # ------------------------------------------------------------------
    capacity_name = get_required_env_var("AZURE_FABRIC_CAPACITY_NAME")
    subscription_id = get_required_env_var("AZURE_SUBSCRIPTION_ID")
    resource_group = get_required_env_var("AZURE_RESOURCE_GROUP")
    solution_suffix = get_required_env_var("SOLUTION_SUFFIX")
    workspace_name = os.getenv(
        "FABRIC_WORKSPACE_NAME", default_workspace_name(solution_suffix)
    )
    workspace_administrators = parse_workspace_administrators(
        get_required_env_var("AZURE_FABRIC_CAPACITY_ADMINISTRATORS"),
        os.getenv("FABRIC_WORKSPACE_ADMINISTRATORS"),
    )
    github_token = os.getenv("GITHUB_TOKEN")

    notebook_path = _notebook_path()

    # ------------------------------------------------------------------
    # Startup banner
    # ------------------------------------------------------------------
    logger.info(f"🏭 {SOLUTION_NAME} – Solution Installer")
    logger.info("=" * 60)
    logger.info(f"Capacity:          {capacity_name}")
    logger.info(f"Subscription:      {subscription_id}")
    logger.info(f"Resource Group:    {resource_group}")
    logger.info(f"Workspace:         {workspace_name}")
    logger.info(f"Solution Suffix:   {solution_suffix}")
    logger.info(f"Installer Notebook: {notebook_path}")
    logger.info(f"GitHub Token:      {'***' if github_token else 'Not set'}")
    if workspace_administrators:
        logger.info(f"Administrators:    {', '.join(workspace_administrators)}")
    logger.info(f"Start time:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Authenticate API clients
    # ------------------------------------------------------------------
    logger.info("\n🔐 Authenticating clients…")
    try:
        fabric_client = create_fabric_client()
        logger.info("   Fabric API client authenticated")
    except Exception as exc:
        logger.error(f"Failed to authenticate Fabric API client: {exc}")
        sys.exit(1)

    try:
        graph_client = create_graph_client()
        logger.info("   Graph API client authenticated")
    except Exception as exc:
        logger.error(f"Failed to authenticate Graph API client: {exc}")
        sys.exit(1)

    executed_steps: list = []
    failed_steps: list = []

    def _abort(step_name: str, error: Exception) -> None:
        """Record the failure, log a summary, and exit."""
        logger.error(f"Exception while executing {step_name}: {error}")
        failed_steps.append({"step": step_name, "error": str(error)})
        completed = {s for s in executed_steps} | {s["step"] for s in failed_steps}
        uncompleted = [s for s in ALL_DEPLOYMENT_STEPS if s not in completed]
        print_steps_summary(SOLUTION_NAME, solution_suffix, executed_steps, failed_steps, uncompleted)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 1 – Set up Fabric workspace
    # ------------------------------------------------------------------
    print_step(1, 4, "Setting up Fabric workspace and capacity assignment",
               capacity_name=capacity_name, workspace_name=workspace_name)
    try:
        workspace_id = setup_workspace(
            fabric_client=fabric_client,
            capacity_name=capacity_name,
            workspace_name=workspace_name,
            subscription_id=subscription_id,
            resource_group=resource_group,
        )
        logger.info("Successfully completed: setup_workspace")
        executed_steps.append("setup_workspace")
    except Exception as exc:
        _abort("setup_workspace", exc)

    # Workspace-scoped client required for all subsequent steps
    logger.info("\nCreating workspace-scoped Fabric API client…")
    try:
        workspace_client = create_workspace_fabric_client(workspace_id)
        logger.info("   Workspace client authenticated")
    except Exception as exc:
        _abort("create_workspace_client", exc)

    # ------------------------------------------------------------------
    # Step 2 – Configure workspace administrators
    # ------------------------------------------------------------------
    admin_display = ", ".join(workspace_administrators) if workspace_administrators else "None"
    print_step(2, 4, "Configuring workspace administrators",
               workspace_id=workspace_id, administrators=admin_display)
    try:
        setup_workspace_administrators(
            workspace_client=workspace_client,
            fabric_admins=workspace_administrators,
            graph_client=graph_client,
        )
        logger.info("Successfully completed: setup_administrators")
        executed_steps.append("setup_administrators")
    except Exception as exc:
        _abort("setup_administrators", exc)

    # ------------------------------------------------------------------
    # Step 3 – Upload installer notebook
    # ------------------------------------------------------------------
    print_step(3, 4, "Uploading installer notebook",
               notebook=INSTALLER_NOTEBOOK_NAME)
    try:
        notebook_id = _upload_installer_notebook(workspace_client, notebook_path, github_token=github_token)
        logger.info("Successfully completed: upload_installer")
        executed_steps.append("upload_installer")
    except Exception as exc:
        _abort("upload_installer", exc)

    # ------------------------------------------------------------------
    # Step 4 – Run installer notebook
    # ------------------------------------------------------------------
    print_step(4, 4, "Running installer notebook",
               notebook_id=notebook_id)
    try:
        _run_installer_notebook(workspace_client, notebook_id)
        logger.info("Successfully completed: run_installer")
        executed_steps.append("run_installer")
    except Exception as exc:
        _abort("run_installer", exc)

    # ------------------------------------------------------------------
    # Success summary
    # ------------------------------------------------------------------
    workspace_url = (
        f"https://app.fabric.microsoft.com/groups/{workspace_id}?experience=fabric-developer"
    )

    print_steps_summary(SOLUTION_NAME, solution_suffix, executed_steps, failed_steps, [])

    logger.info(f"\n{'='*60}")
    logger.info(f"🎉 {SOLUTION_NAME.upper()} INSTALLATION COMPLETE!")
    logger.info(f"{'='*60}")
    logger.info(f"Completed:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Suffix:     {solution_suffix}")
    logger.info(f"Workspace:  {workspace_name}")
    logger.info(f"URL:        {workspace_url}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n\nInstallation interrupted by user")
        sys.exit(1)
    except Exception as exc:
        logger.error(f"\n\nUnexpected error: {exc}")
        sys.exit(1)
