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
    python install_microsoft_iq_solution.py

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

import json
import logging
import os
import sys
from datetime import datetime

# Add infra/scripts/ to path so the fabric package and its modules can be imported
sys.path.append(os.path.dirname(__file__))

from fabric.helpers.logging_config import setup_logging

# Configure logging before any other imports so that library modules
# (fabric_api, graph_api, helpers.*) inherit the root logger's settings.
# The log level can be set via ``azd env set LOG_LEVEL DEBUG``.
setup_logging()

# Module-level logger for this entry-point script.  All log calls below
# use this logger; the level and handler are inherited from setup_logging().
logger = logging.getLogger(__name__)

from fabric.fabric_api import FabricApiError, create_fabric_client, create_workspace_fabric_client
from fabric.graph_api import create_graph_client
from fabric.helpers.config import SOLUTION_NAME, default_workspace_name
from fabric.helpers.utils import (
    INSTALLER_NOTEBOOK_NAME,
    get_notebook_path,
    run_installer_notebook,
    upload_installer_notebook,
    get_required_env_var,
    parse_workspace_administrators,
    print_step,
    print_steps_summary,
)
from fabric.helpers.workspace import setup_workspace
from fabric.helpers.workspace_admins import setup_workspace_administrators


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALL_DEPLOYMENT_STEPS = [
    "setup_workspace",
    "setup_administrators",
    "upload_installer",
    "run_installer",
]


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

    notebook_path = get_notebook_path()

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
        notebook_id = upload_installer_notebook(workspace_client, notebook_path, github_token=github_token)
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
        run_installer_notebook(workspace_client, notebook_id)
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
