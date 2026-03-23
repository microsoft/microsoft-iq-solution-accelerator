#!/usr/bin/env python3
"""
Unified Data Foundation Solution Installer

This script provides a simplified deployment entry-point for the Unified Data Foundation
solution. It performs only the minimum steps needed to bootstrap the solution:

    1. setup_workspace        - Create and configure the Fabric workspace/capacity
    2. setup_administrators   - Add workspace administrators
    3. upload_installer       - Upload the installer notebook to the workspace
    4. run_installer          - Execute the installer notebook end-to-end

The installer notebook (udf_solution_installer.ipynb) handles the remaining
solution-specific steps (lakehouse creation, data ingestion, notebook deployment,
post-deployment tasks, …) once it has been uploaded and started.

Usage:
    python install_udf_solution.py

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
"""

import os
import sys
from datetime import datetime

# Add current directory to path so local modules can be imported
sys.path.append(os.path.dirname(__file__))

from fabric_api import FabricApiError, create_fabric_client, create_workspace_fabric_client
from graph_api import create_graph_client
from helpers.config import REPO_ROOT, SOLUTION_NAME, default_workspace_name
from helpers.utils import (
    encode_notebook,
    get_required_env_var,
    parse_workspace_administrators,
    print_step,
    print_steps_summary,
)
from helpers.udf_workspace import setup_workspace
from helpers.udf_workspace_admins import setup_workspace_administrators


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

    The notebook lives at ``<repo-root>/fabric/infra/deploy/fabric_solution_installer.ipynb``.
    """
    return os.path.join(REPO_ROOT, "fabric", "infra", "deploy", f"{INSTALLER_NOTEBOOK_NAME}.ipynb")


def _upload_installer_notebook(workspace_client, notebook_path: str) -> str:
    """Upload (or update) the installer notebook in the workspace.

    If a notebook with the same name already exists it will be updated in-place;
    otherwise a new notebook is created.

    Args:
        workspace_client: Authenticated :class:`FabricWorkspaceApiClient`.
        notebook_path: Absolute path to the local ``.ipynb`` file.

    Returns:
        str: The notebook ID of the uploaded/updated notebook.

    Raises:
        FileNotFoundError: If the notebook file does not exist.
        FabricApiError: If the Fabric API call fails.
    """
    print(f"   Reading notebook file: {notebook_path}")
    notebook_base64 = encode_notebook(notebook_path)

    print(f"   Checking for existing notebook: {INSTALLER_NOTEBOOK_NAME}")
    existing = workspace_client.get_notebook_by_name(INSTALLER_NOTEBOOK_NAME)

    if existing:
        notebook_id = existing["id"]
        print(f"   ℹ️  Notebook already exists ({notebook_id}) – updating definition")
        workspace_client.update_notebook(notebook_id, notebook_base64)
        print(f"   ✅ Notebook updated: {INSTALLER_NOTEBOOK_NAME}")
    else:
        print(f"   Creating notebook: {INSTALLER_NOTEBOOK_NAME}")
        workspace_client.create_notebook(INSTALLER_NOTEBOOK_NAME, notebook_base64)
        refreshed = workspace_client.get_notebook_by_name(INSTALLER_NOTEBOOK_NAME)
        if not refreshed:
            raise FabricApiError(
                f"Notebook '{INSTALLER_NOTEBOOK_NAME}' was not found after creation"
            )
        notebook_id = refreshed["id"]
        print(f"   ✅ Notebook created: {INSTALLER_NOTEBOOK_NAME} ({notebook_id})")

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
    print(f"   Scheduling notebook job: {INSTALLER_NOTEBOOK_NAME} ({notebook_id})")
    result = workspace_client.schedule_notebook_job(notebook_id, monitor_interval=monitor_interval)

    status = result.get("status", "Unknown")
    duration = result.get("duration", "N/A")

    print(f"   📊 Execution result:")
    print(f"      Status:   {status}")
    print(f"      Duration: {duration}")

    if status != "Completed":
        error_detail = result.get("error", "No error details available")
        raise FabricApiError(
            f"Installer notebook finished with status '{status}'. Error: {error_detail}"
        )

    print(f"   ✅ Installer notebook completed successfully")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Orchestrate the minimal three-step solution installation."""

    # ------------------------------------------------------------------
    # Configuration from environment variables
    # ------------------------------------------------------------------
    capacity_name = get_required_env_var("AZURE_FABRIC_CAPACITY_NAME")
    solution_suffix = get_required_env_var("SOLUTION_SUFFIX")
    workspace_name = os.getenv(
        "FABRIC_WORKSPACE_NAME", default_workspace_name(solution_suffix)
    )
    workspace_administrators = parse_workspace_administrators(
        get_required_env_var("AZURE_FABRIC_CAPACITY_ADMINISTRATORS"),
        os.getenv("FABRIC_WORKSPACE_ADMINISTRATORS"),
    )

    notebook_path = _notebook_path()

    # ------------------------------------------------------------------
    # Startup banner
    # ------------------------------------------------------------------
    print(f"🏭 {SOLUTION_NAME} – Solution Installer")
    print("=" * 60)
    print(f"Capacity:          {capacity_name}")
    print(f"Workspace:         {workspace_name}")
    print(f"Solution Suffix:   {solution_suffix}")
    print(f"Installer Notebook:{notebook_path}")
    if workspace_administrators:
        print(f"Administrators:    {', '.join(workspace_administrators)}")
    print(f"Start time:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Authenticate API clients
    # ------------------------------------------------------------------
    print("\n🔐 Authenticating clients…")
    try:
        fabric_client = create_fabric_client()
        print("   ✅ Fabric API client authenticated")
    except Exception as exc:
        print(f"   ❌ Failed to authenticate Fabric API client: {exc}")
        sys.exit(1)

    try:
        graph_client = create_graph_client()
        print("   ✅ Graph API client authenticated")
    except Exception as exc:
        print(f"   ❌ Failed to authenticate Graph API client: {exc}")
        sys.exit(1)

    executed_steps: list = []
    failed_steps: list = []

    def _abort(step_name: str, error: Exception) -> None:
        """Record the failure, print a summary, and exit."""
        print(f"❌ Exception while executing {step_name}: {error}")
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
        )
        print("✅ Successfully completed: setup_workspace")
        executed_steps.append("setup_workspace")
    except Exception as exc:
        _abort("setup_workspace", exc)

    # Workspace-scoped client required for all subsequent steps
    print("\n🔐 Creating workspace-scoped Fabric API client…")
    try:
        workspace_client = create_workspace_fabric_client(workspace_id)
        print("   ✅ Workspace client authenticated")
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
        print("✅ Successfully completed: setup_administrators")
        executed_steps.append("setup_administrators")
    except Exception as exc:
        _abort("setup_administrators", exc)

    # ------------------------------------------------------------------
    # Step 3 – Upload installer notebook
    # ------------------------------------------------------------------
    print_step(3, 4, "Uploading installer notebook",
               notebook=INSTALLER_NOTEBOOK_NAME)
    try:
        notebook_id = _upload_installer_notebook(workspace_client, notebook_path)
        print("✅ Successfully completed: upload_installer")
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
        print("✅ Successfully completed: run_installer")
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

    print(f"\n{'='*60}")
    print(f"🎉 {SOLUTION_NAME.upper()} INSTALLATION COMPLETE!")
    print(f"{'='*60}")
    print(f"📅 Completed:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏷️  Suffix:     {solution_suffix}")
    print(f"☁️  Workspace:  {workspace_name}")
    print(f"🔗 URL:        {workspace_url}")
    print(f"{'='*60}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation interrupted by user")
        sys.exit(1)
    except Exception as exc:
        print(f"\n\n❌ Unexpected error: {exc}")
        sys.exit(1)
